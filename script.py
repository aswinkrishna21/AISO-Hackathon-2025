
# Create the project structure overview
project_structure = """
elderly-voice-agent/
├── frontend/
│   ├── agent.py              # Main Pipecat voice agent
│   ├── requirements.txt       # Frontend dependencies
│   └── config.py             # Configuration settings
├── backend/
│   ├── app.py                # Main Flask server
│   ├── messaging_service.py  # Messaging logic
│   ├── call_service.py       # Call/videocall logic
│   ├── notification_service.py  # Notification management
│   ├── requirements.txt       # Backend dependencies
│   └── config.py             # Backend configuration
├── .env.example              # Environment variables template
└── README.md                 # Project documentation
"""

print("PROJECT STRUCTURE")
print("=" * 80)
print(project_structure)
print("\n" + "=" * 80)
