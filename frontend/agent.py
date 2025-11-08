"""
Voice Agent for Elderly Communication
Uses Pipecat framework to create a voice-controlled communication assistant
"""

import os
import asyncio
from pipecat.frames.frames import TextFrame, EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_response import LLMAssistantResponseAggregator, LLMUserResponseAggregator
# from pipecat.services.deepgram import DeepgramSTTService
# from pipecat.services.openai import OpenAILLMService
# from pipecat.services.cartesia import CartesiaTTSService
# from pipecat.transports.services.daily import DailyTransport, DailyParams
# from pipecat.vad.silero import SileroVADAnalyzer
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.transports.daily.transport import DailyTransport, DailyParams
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.services.perplexity.llm import PerplexityLLMService

import aiohttp
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Backend API endpoint
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


class ElderlyVoiceAgent:
    """Voice agent specifically designed for elderly users"""

    def __init__(self):
        self.session = None

    async def send_message(self, contact_name: str, message: str):
        """Send a message through backend API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/api/messages/send",
                    json={"contact": contact_name, "message": message}
                ) as response:
                    result = await response.json()
                    return result.get("status") == "success"
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    async def request_call(self, contact_name: str, call_type: str):
        """Request a voice or video call"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/api/calls/request",
                    json={"contact": contact_name, "type": call_type}
                ) as response:
                    result = await response.json()
                    return result.get("status") == "success"
        except Exception as e:
            logger.error(f"Error requesting call: {e}")
            return False

    async def handle_call_response(self, call_id: str, accept: bool):
        """Accept or reject an incoming call"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/api/calls/respond",
                    json={"call_id": call_id, "accept": accept}
                ) as response:
                    result = await response.json()
                    return result.get("status") == "success"
        except Exception as e:
            logger.error(f"Error responding to call: {e}")
            return False


async def create_daily_token(room_name: str, api_key: str) -> str:
    """Create a Daily meeting token for the given room."""
    if not room_name or not api_key:
        raise ValueError("DAILY_ROOM_NAME or DAILY_API_KEY missing.")
    url = "https://api.daily.co/v1/meeting-tokens"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "properties": {
            "room_name": room_name,
            "is_owner": True
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(f"Daily token error {resp.status}: {data}")
            return data["token"]


async def main():
    """Main entry point for the voice agent"""

    daily_api_key = os.getenv("DAILY_API_KEY")
    daily_room_name = os.getenv("DAILY_ROOM_NAME")
    token = await create_daily_token(daily_room_name, daily_api_key)
    DAILY_ROOM_URL = "https://eldervoiceagent.daily.co/ElderlyVoiceAssistantRoom"
    #DAILY_ROOM_URL = f"https://{daily_room_name}.daily.co"

    # Initialize transport (Daily for WebRTC)
    transport = DailyTransport(
        params = DailyParams(
            api_key=os.getenv("DAILY_API_KEY"),
            audio_in_enabled=True,
            audio_out_enabled=True,
            transcription_enabled=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer()
        ),
        token=token,
        room_url=DAILY_ROOM_URL,
        bot_name="ElderlyVoiceAssistant"
    )

    # Initialize STT service (Deepgram)
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2",
        language="en"
    )

    # Initialize LLM service (OpenAI)
    llm = PerplexityLLMService(api_key=os.getenv("PERPLEXITY_API_KEY"), model="sonar")
    # llm = OpenAILLMService(
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     model="gpt-4",
    # )

    # Initialize TTS service (Cartesia)
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091"  # Friendly, clear voice
    )

    # Define system prompt for elderly-friendly interaction
    system_prompt = """You are a friendly and patient voice assistant designed specifically for elderly users. 
Your role is to help them communicate with family and friends without needing to use phones or computers directly.

You can help them:
1. Send text messages to their contacts (e.g., "Send a message to John saying I miss you")
2. Request voice calls or video calls (e.g., "Call Sarah on video" or "Make a voice call to Michael")
3. Notify them of new messages (e.g., "You have a new message from Emma")
4. Handle incoming calls (e.g., "Accept the call from David" or "Decline the call")

IMPORTANT GUIDELINES:
- Speak slowly and clearly
- Use simple, everyday language
- Confirm actions before executing them
- Be patient and repeat information if needed
- Always confirm the person's name before sending messages or making calls
- Provide clear feedback about what's happening

When the user wants to send a message, extract:
- Contact name
- Message content

When the user wants to make a call, extract:
- Contact name
- Call type (voice or video)

For incoming notifications, clearly announce:
- Who is calling or who sent a message
- Wait for the user's response

Be warm, friendly, and respectful at all times."""

    # Create response aggregators
    llm_user_aggregator = LLMUserResponseAggregator()
    llm_assistant_aggregator = LLMAssistantResponseAggregator()

    # Create pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        llm_user_aggregator,
        llm,
        tts,
        transport.output(),
        llm_assistant_aggregator
    ])

    # Create and run task
    task = PipelineTask(
        pipeline,
        params = PipelineParams(
                system_prompt= system_prompt
        ),
        observers=[]
    )

    # Start the agent
    runner = PipelineRunner()
    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
