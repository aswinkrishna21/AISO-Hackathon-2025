import os
import json
import asyncio
import base64
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.responses import HTMLResponse

# Pipecat imports
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame, AudioRawFrame, TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.services.perplexity.llm import PerplexityLLMService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketTransport,
    FastAPIWebsocketParams,
)
from pipecat.transports.serializers.fastapi_websocket_serializer import FastAPIWebsocketSerializer


from system_prompt import SYSTEM_PROMPT
from tools import get_tools

from pipecat.processors.frame_processor import FrameProcessor

class FrameLogger(FrameProcessor):
    async def process_frame(self, frame, direction):
        # Print type of frame
        print(f"[FRAME] {type(frame).__name__}")

        # Print additional info depending on frame type
        if isinstance(frame, TextFrame):
            print(f"  Text: {frame.text}")
        elif isinstance(frame, AudioRawFrame):
            print(f"  Audio length: {len(frame.audio)} bytes, Sample rate: {frame.sample_rate}")
        else:
            print(f"  Other frame: {frame}")

        return await super().process_frame(frame, direction)


# ---------------- LOGGERS ---------------- #
class InputLogger(FrameProcessor):
    async def process_frame(self, frame, direction):
        print(f"[INPUT] {type(frame).__name__}")
        return await super().process_frame(frame, direction)


class TranscriptionLogger(FrameProcessor):
    async def process_frame(self, frame, direction):
        if isinstance(frame, TextFrame):
            print(f"[TRANSCRIPTION] {frame.text}")
        return await super().process_frame(frame, direction)


# ---------------- CUSTOM RN INTERCEPTOR ---------------- #
class ReactNativeInputInterceptor(FrameProcessor):
    """
    Handles base64 audio or text JSON *after* the transport receives them.
    The transport converts WebSocket messages → TextFrame or AudioRawFrame automatically.
    """

    async def process_frame(self, frame, direction):
        if isinstance(frame, TextFrame):
            txt = frame.text.strip()
            if txt.lower() == "stop":
                print("🛑 Received stop command (ignored, Pipecat handles control flow)")
            else:
                print(f"[RN TEXT] {txt}")

        elif isinstance(frame, AudioRawFrame):
            print(f"[RN AUDIO] {len(frame.audio)} bytes")

        return await super().process_frame(frame, direction)


# ---------------- MAIN APP ---------------- #
load_dotenv(override=True)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    html = """
    <!DOCTYPE html>
    <html>
        <head><title>WebSocket Audio Test</title></head>
        <body>
            <h1>WebSocket connection test</h1>
            <script>
                const ws = new WebSocket("ws://" + window.location.host + "/ws");
                ws.onopen = () => console.log("Connected");
                ws.onmessage = e => console.log("Message:", e.data);
                ws.onclose = () => console.log("Closed");
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html)


# ---------------- BOT STREAM ---------------- #
async def run_bot_stream(websocket_client: WebSocket):
    print("Starting live audio stream bot...")

    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=FastAPIWebsocketSerializer(),
        ),
    )

    # AI services
    llm = PerplexityLLMService(api_key=os.getenv("PERPLEXITY_API_KEY"), model="sonar")
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"), audio_passthrough=True)
    tts = DeepgramTTSService(api_key=os.getenv("DEEPGRAM_API_KEY"), voice="aura-2-andromeda-en")

    # Context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    # Pipeline
    pipeline = Pipeline(
        [
            transport.input(),
            FrameLogger(),
            InputLogger(),
            ReactNativeInputInterceptor(),   # ✅ Your custom handler
            InputLogger(),
            stt,
            TranscriptionLogger(),
            context_aggregator.user(),
            llm,
            tts,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=16000,
            audio_out_sample_rate=16000,
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
        )
    )

    runner = PipelineRunner(handle_sigint=False, force_gc=True)

    # Start the pipeline (it now owns the websocket)
    print("✅ Starting pipeline...")
    pipeline_task = asyncio.create_task(runner.run(task))

    # Warm-up: send initial message
    await asyncio.sleep(0.5)
    messages.append({"role": "user", "content": "Hello, please introduce yourself."})
    await task.queue_frames([LLMRunFrame()])

    # Wait until pipeline exits (user disconnect, error, etc.)
    try:
        await pipeline_task
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Pipeline error: {e}")

    print("Pipeline closed.")


# ---------------- ENDPOINT ---------------- #
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket connection accepted.")
    await run_bot_stream(websocket)


# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    import uvicorn

    print("Starting server...")
    print(f"PERPLEXITY API: {'Set' if os.getenv('PERPLEXITY_API_KEY') else 'NOT SET'}")
    print(f"DEEPGRAM API: {'Set' if os.getenv('DEEPGRAM_API_KEY') else 'NOT SET'}")

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8765")))
