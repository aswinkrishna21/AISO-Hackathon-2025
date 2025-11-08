
# Create configuration files

# frontend/config.py
frontend_config = """\"\"\"
Frontend Configuration
\"\"\"

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    \"\"\"Configuration for the voice agent\"\"\"
    
    # API Keys
    DAILY_API_KEY = os.getenv('DAILY_API_KEY', '')
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    CARTESIA_API_KEY = os.getenv('CARTESIA_API_KEY', '')
    
    # Backend URL
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
    
    # Daily.co settings
    DAILY_ROOM_URL = os.getenv('DAILY_ROOM_URL', '')
    
    # Agent settings
    AGENT_VOICE_ID = os.getenv('AGENT_VOICE_ID', 'a0e99841-438c-4a64-b679-ae501e7d6091')
    AGENT_LANGUAGE = os.getenv('AGENT_LANGUAGE', 'en')
    
    # LLM settings
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
"""

with open("elderly-voice-agent/frontend/config.py", "w") as f:
    f.write(frontend_config)

print("Created frontend/config.py")

# backend/config.py
backend_config = """\"\"\"
Backend Configuration
\"\"\"

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    \"\"\"Configuration for the backend server\"\"\"
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Daily.co API settings
    DAILY_API_KEY = os.getenv('DAILY_API_KEY', '')
    DAILY_DOMAIN = os.getenv('DAILY_DOMAIN', '')
    
    # Database settings (for future use)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///elderly_agent.db')
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
"""

with open("elderly-voice-agent/backend/config.py", "w") as f:
    f.write(backend_config)

print("Created backend/config.py")
