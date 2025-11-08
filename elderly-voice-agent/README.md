# Elderly Voice Agent

An AI-powered voice communication assistant designed specifically for elderly users, enabling them to send messages, make calls, and manage communications without needing to use phones or other technological devices directly.

## 🎯 Features

- **Voice-Controlled Messaging**: Send text messages to contacts using natural voice commands
- **Voice & Video Calls**: Initiate and receive voice or video calls through simple voice requests
- **Incoming Call Management**: Accept or reject calls using voice commands
- **Message Notifications**: Receive audio notifications about new messages
- **Hands-Free Operation**: Complete communication without touching any device
- **Elderly-Friendly Design**: Patient, clear, and simple interactions

## 🏗️ Architecture

The system consists of two main components:

### Frontend (Voice Agent)
- Built with **Pipecat** framework for real-time voice AI
- Uses **Deepgram** for Speech-to-Text
- Uses **OpenAI GPT-4** for natural language understanding
- Uses **Cartesia** for Text-to-Speech
- Uses **Daily.co** for WebRTC transport

### Backend (Communication Server)
- Built with **Flask** and **Flask-SocketIO**
- Handles messaging, calls, and notifications
- Real-time WebSocket communication
- RESTful API for agent interactions

```
elderly-voice-agent/
├── frontend/              # Voice agent (Pipecat)
│   ├── agent.py          # Main voice agent
│   ├── config.py         # Configuration
│   └── requirements.txt  # Dependencies
├── backend/              # Communication server (Flask)
│   ├── app.py           # Main Flask server
│   ├── messaging_service.py   # Messaging logic
│   ├── call_service.py        # Call management
│   ├── notification_service.py # Notifications
│   ├── config.py         # Configuration
│   └── requirements.txt  # Dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 📋 Prerequisites

- Python 3.10 or higher
- API Keys for:
  - [Daily.co](https://www.daily.co/) (WebRTC)
  - [Deepgram](https://www.deepgram.com/) (Speech-to-Text)
  - [OpenAI](https://platform.openai.com/) (LLM)
  - [Cartesia](https://cartesia.ai/) (Text-to-Speech)

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd elderly-voice-agent
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
DAILY_API_KEY=your_daily_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CARTESIA_API_KEY=your_cartesia_api_key_here
```

### 3. Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd ../frontend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🎮 Usage

### Starting the Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The backend server will start on `http://localhost:5000`

### Starting the Voice Agent

```bash
cd frontend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python agent.py
```

## 💬 Voice Commands

The agent understands natural language. Here are example commands:

### Sending Messages
- "Send a message to John saying I miss you"
- "Tell Sarah I'll call her tomorrow"
- "Message Michael: How are you doing?"

### Making Calls
- "Call Emma"
- "Make a video call to David"
- "Start a voice call with Sarah"

### Managing Incoming Calls
- "Accept the call"
- "Reject the call from John"
- "I don't want to take this call"

### Checking Messages
- "Do I have any new messages?"
- "Read my messages from Sarah"

## 🔧 API Endpoints

### Messaging

- `POST /api/messages/send` - Send a message
- `GET /api/messages/history` - Get message history

### Calls

- `POST /api/calls/request` - Request a call
- `POST /api/calls/respond` - Accept/reject a call
- `POST /api/calls/end` - End an active call

### WebSocket Events

- `connect` - Client connection
- `register` - Register user with session
- `new_message` - New message notification
- `incoming_call` - Incoming call notification
- `call_accepted` - Call accepted notification
- `call_rejected` - Call rejected notification

## 🎨 Customization

### Changing the Voice

Edit `frontend/config.py` and change the `AGENT_VOICE_ID`:

```python
AGENT_VOICE_ID = 'your_preferred_voice_id'
```

Available Cartesia voices can be found in their [documentation](https://docs.cartesia.ai/).

### Adjusting Agent Behavior

Edit the `system_prompt` in `frontend/agent.py` to customize how the agent responds.

### Adding More Features

The modular architecture makes it easy to add new features:

1. Add new service in `backend/` (e.g., `calendar_service.py`)
2. Add API endpoints in `backend/app.py`
3. Update the agent's system prompt to handle new commands

## 🔒 Security Considerations

**Important for Production:**

1. **API Keys**: Never commit `.env` files. Use secure key management.
2. **Authentication**: Add user authentication before deploying.
3. **Database**: Replace in-memory storage with a proper database (PostgreSQL, MongoDB).
4. **HTTPS**: Use HTTPS for all communications.
5. **Rate Limiting**: Implement rate limiting to prevent abuse.
6. **Input Validation**: Add comprehensive input validation.

## 🐛 Troubleshooting

### Agent doesn't respond to voice

- Check that your microphone is working
- Verify DEEPGRAM_API_KEY is valid
- Check backend server is running

### Calls don't connect

- Verify DAILY_API_KEY is valid
- Check that Daily.co room creation is working
- Ensure WebSocket connection is established

### Messages not being delivered

- Verify backend server is running
- Check WebSocket connection status
- Review server logs for errors

## 📚 Dependencies

### Frontend
- pipecat-ai - Voice AI framework
- deepgram-sdk - Speech-to-Text
- openai - Language model
- cartesia - Text-to-Speech
- daily-python - WebRTC transport

### Backend
- Flask - Web framework
- Flask-SocketIO - WebSocket support
- Flask-CORS - CORS handling
- requests - HTTP client

## 🤝 Contributing

This is a hackathon project. Feel free to fork and modify for your needs!

## 📄 License

MIT License - feel free to use this project for your hackathon or personal projects.

## 🎯 Hackathon Tips

1. **Demo Script**: Prepare a demo showing all key features
2. **Test Thoroughly**: Test all voice commands before presenting
3. **Backup Plan**: Have a video demo ready in case of technical issues
4. **Explain the Impact**: Focus on how this helps elderly users
5. **Show Scalability**: Explain how to add database, authentication, etc.

## 📞 Support

For questions or issues during the hackathon, check:
- Pipecat documentation: https://docs.pipecat.ai/
- Daily.co documentation: https://docs.daily.co/
- Flask-SocketIO documentation: https://flask-socketio.readthedocs.io/

## 🌟 Future Enhancements

- Database integration for persistent storage
- User authentication and profiles
- Contact management system
- Calendar integration
- Medication reminders
- Emergency contact features
- Multi-language support
- Mobile app integration

Good luck with your hackathon! 🚀
