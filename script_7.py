
# Create requirements files and configuration files

# frontend/requirements.txt
frontend_requirements = """# Pipecat and related dependencies
pipecat-ai>=0.0.40
python-dotenv>=1.0.0
aiohttp>=3.9.0
loguru>=0.7.0

# Speech-to-Text
deepgram-sdk>=3.0.0

# Text-to-Speech
cartesia>=1.0.0

# LLM
openai>=1.0.0

# Daily.co for WebRTC transport
daily-python>=0.10.0

# VAD
silero-vad>=4.0.0
"""

with open("elderly-voice-agent/frontend/requirements.txt", "w") as f:
    f.write(frontend_requirements)

print("Created frontend/requirements.txt")

# backend/requirements.txt
backend_requirements = """# Flask and web server
Flask>=3.0.0
Flask-SocketIO>=5.3.0
Flask-CORS>=4.0.0

# WebSocket support
python-socketio>=5.10.0
eventlet>=0.33.0

# Environment variables
python-dotenv>=1.0.0

# HTTP requests
requests>=2.31.0

# Daily.co API
requests>=2.31.0
"""

with open("elderly-voice-agent/backend/requirements.txt", "w") as f:
    f.write(backend_requirements)

print("Created backend/requirements.txt")
