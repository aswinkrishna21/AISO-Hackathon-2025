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
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.perplexity.llm import PerplexityLLMService
# Services
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService

# FastAPI Websocket transport (no Twilio)
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketTransport,
    FastAPIWebsocketParams,
)

# Project-specific tools
from tools import get_tools
from system_prompt import SYSTEM_PROMPT


# Custom processor to log transcribed text
class TranscriptionLogger(FrameProcessor):
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, TextFrame):
            print(f"🎤 TRANSCRIBED TEXT: '{frame.text}'")
        elif isinstance(frame, AudioRawFrame):
            print(f"🔊 AUDIO FRAME: {len(frame.audio)} bytes, {frame.sample_rate}Hz, {frame.num_channels} channels")
            
        return frame


# Custom processor to log all input frames
class InputLogger(FrameProcessor):
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, AudioRawFrame):
            print(f"📥 INPUT AUDIO: {len(frame.audio)} bytes at {frame.sample_rate}Hz")
        elif isinstance(frame, TextFrame):
            print(f"📥 INPUT TEXT: '{frame.text}'")
        else:
            print(f"📥 INPUT FRAME: {type(frame).__name__}")
            
        return frame


load_dotenv(override=True)
app = FastAPI()

# Add CORS for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    """Simple HTML test page for manual connection."""
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


# Custom frame processor to handle React Native data
class ReactNativeFrameProcessor:
    def __init__(self, task):
        self.task = task

    async def process_message(self, data):
        """Process incoming WebSocket message and convert to frames"""
        try:
            if isinstance(data, bytes):
                # Binary audio data
                print(f"Received {len(data)} bytes of audio data")
                audio_frame = AudioRawFrame(
                    audio=data,
                    sample_rate=16000,
                    num_channels=1
                )
                await self.task.queue_frames([audio_frame])
                
            elif isinstance(data, str):
                print(f"Received text: {data[:100]}...")
                
                try:
                    # Try to parse as JSON
                    json_data = json.loads(data)
                    
                    # Handle base64 encoded audio
                    if "audio" in json_data:
                        audio_b64 = json_data["audio"]
                        audio_bytes = base64.b64decode(audio_b64)
                        print(f"Decoded {len(audio_bytes)} bytes from base64 audio")
                        
                        audio_frame = AudioRawFrame(
                            audio=audio_bytes,
                            sample_rate=16000,
                            num_channels=1
                        )
                        await self.task.queue_frames([audio_frame])
                    
                    # Handle text messages as direct input
                    elif "text" in json_data:
                        text_content = json_data["text"]
                        print(f"Processing text input: {text_content}")
                        text_frame = TextFrame(text=text_content)
                        await self.task.queue_frames([text_frame])
                    
                    # Handle control messages
                    elif "command" in json_data:
                        cmd = json_data["command"].lower()
                        if cmd == "stop":
                            print("Received stop command")
                            return False  # Signal to stop
                
                except json.JSONDecodeError:
                    # Plain text - treat as direct user input
                    if data.strip().lower() == "stop":
                        print("Received stop command")
                        return False
                    else:
                        print(f"Processing plain text input: {data}")
                        text_frame = TextFrame(text=data.strip())
                        await self.task.queue_frames([text_frame])
            
            return True  # Continue processing
            
        except Exception as e:
            print(f"Error processing message: {e}")
            import traceback
            traceback.print_exc()
            return True


async def run_bot_stream(websocket_client: WebSocket):
    print("Starting live audio stream bot...")

    # Custom transport params for React Native
    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=None,  # No Twilio serializer
        ),
    )

    # AI Services - using Perplexity with simplified context (no tools for now)
    llm = PerplexityLLMService(api_key=os.getenv("PERPLEXITY_API_KEY"), model="sonar")
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"), audio_passthrough=True)
    tts = DeepgramTTSService(api_key=os.getenv("DEEPGRAM_API_KEY"), voice="aura-2-andromeda-en")

    # Initialize conversation context - Perplexity needs simpler message format
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    # Create proper context object for Perplexity (no tools)
    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    # Add loggers for debugging
    input_logger = InputLogger()
    transcription_logger = TranscriptionLogger()

    pipeline = Pipeline(
        [
            transport.input(),
            input_logger,       # Log all input frames first
            stt,
            transcription_logger,  # Log transcribed text here
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
            audio_in_sample_rate=16000,  # React Native standard
            audio_out_sample_rate=16000,
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    runner = PipelineRunner(handle_sigint=False, force_gc=True)

    # Create frame processor
    frame_processor = ReactNativeFrameProcessor(task)

    # Start pipeline in background
    print("Starting pipeline...")
    pipeline_task = asyncio.create_task(runner.run(task))
    
    # Send welcome message after a brief delay to ensure pipeline is ready
    await asyncio.sleep(0.5)
    # Add a user message first to satisfy Perplexity's requirements
    messages.append({"role": "user", "content": "Hello, please introduce yourself."})
    await task.queue_frames([LLMRunFrame()])
    print("Pipeline started and welcome message queued")

    # Let the transport handle the WebSocket, but we can still process custom messages
    # by using the transport's message handling capabilities
    try:
        # Just wait for the pipeline to complete
        # The transport will handle all WebSocket communication
        await pipeline_task
        
    except Exception as e:
        print(f"Error in pipeline: {e}")
        import traceback
        traceback.print_exc()

    print("Pipeline completed")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted from React Native app")
    try:
        await run_bot_stream(websocket)
    except Exception as e:
        print(f"Error in websocket endpoint: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    
    print("Starting server...")
    print(f"OpenAI API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
    print(f"Deepgram API Key: {'Set' if os.getenv('DEEPGRAM_API_KEY') else 'NOT SET'}")
    
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8765")))