
# Create .env.example file
env_example = """# ==============================================
# Elderly Voice Agent - Environment Variables
# ==============================================

# Backend Server Settings
SECRET_KEY=your-secret-key-change-in-production
PORT=5000
HOST=0.0.0.0
DEBUG=False
BACKEND_URL=http://localhost:5000

# Daily.co Settings (for WebRTC)
# Sign up at https://www.daily.co/ to get these
DAILY_API_KEY=your_daily_api_key_here
DAILY_DOMAIN=your_daily_domain_here
DAILY_ROOM_URL=

# Deepgram Settings (Speech-to-Text)
# Sign up at https://www.deepgram.com/ to get API key
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# OpenAI Settings (Language Model)
# Get API key from https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7

# Cartesia Settings (Text-to-Speech)
# Sign up at https://cartesia.ai/ to get API key
CARTESIA_API_KEY=your_cartesia_api_key_here
AGENT_VOICE_ID=a0e99841-438c-4a64-b679-ae501e7d6091

# Agent Settings
AGENT_LANGUAGE=en

# CORS Settings
CORS_ORIGINS=*

# Database (for future use)
DATABASE_URL=sqlite:///elderly_agent.db
"""

with open("elderly-voice-agent/.env.example", "w") as f:
    f.write(env_example)

print("Created .env.example")
