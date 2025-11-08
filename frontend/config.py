"""
Frontend Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration for the voice agent"""

    # API Keys
    DAILY_API_KEY = os.getenv('DAILY_API_KEY', '')
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    CARTESIA_API_KEY = os.getenv('CARTESIA_API_KEY', '')

    # Backend URL
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

    # Daily.co settings
    DAILY_ROOM_URL = os.getenv('DAILY_ROOM_URL', '')

    # Agent settings
    AGENT_VOICE_ID = os.getenv('AGENT_VOICE_ID', 'a0e99841-438c-4a64-b679-ae501e7d6091')
    AGENT_LANGUAGE = os.getenv('AGENT_LANGUAGE', 'en')

    # LLM settings
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
