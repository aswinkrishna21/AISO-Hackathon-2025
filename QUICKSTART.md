# Quick Start Guide - Elderly Voice Agent

## ⚡ Get Running in 5 Steps

### Step 1: Get Your API Keys (10 minutes)

Visit these websites and sign up for free accounts:

1. **Daily.co** (https://www.daily.co/)
   - Sign up for free account
   - Go to Dashboard → Developers
   - Copy your API Key

2. **Deepgram** (https://www.deepgram.com/)
   - Sign up and get $200 free credits
   - Go to API Keys
   - Create and copy a new API key

3. **OpenAI** (https://platform.openai.com/)
   - Sign up (requires payment method)
   - Go to API Keys
   - Create and copy a new API key

4. **Cartesia** (https://cartesia.ai/)
   - Sign up for early access
   - Get your API key from dashboard

### Step 2: Configure Your Environment (2 minutes)

```bash
cd elderly-voice-agent
cp .env.example .env
```

Edit `.env` with your favorite text editor and paste your API keys:

```env
DAILY_API_KEY=your_actual_key_here
DEEPGRAM_API_KEY=your_actual_key_here
OPENAI_API_KEY=your_actual_key_here
CARTESIA_API_KEY=your_actual_key_here
```

### Step 3: Install Backend (3 minutes)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Install Frontend (3 minutes)

Open a NEW terminal window:

```bash
cd frontend
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 5: Run Everything (1 minute)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

You should see: `Running on http://0.0.0.0:5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
source venv/bin/activate
python agent.py
```

The voice agent will start listening!

## 🎤 Testing Voice Commands

Try saying these commands:

1. **"Send a message to John saying hello"**
   - The agent should confirm and send the message

2. **"Call Sarah"**
   - The agent should initiate a voice call

3. **"Make a video call to Michael"**
   - The agent should start a video call

## 🔧 Troubleshooting

### Backend won't start
- **Error:** Port 5000 already in use
  - **Solution:** Change PORT in .env to 5001

### Agent doesn't hear me
- **Check:** Microphone permissions
- **Check:** Deepgram API key is correct
- **Try:** Speaking louder and clearer

### API Key errors
- **Check:** No extra spaces in .env file
- **Check:** Keys are copied completely
- **Try:** Regenerate keys if needed

## 📝 Demo Script for Hackathon

**Introduction (30 seconds):**
"We built an AI voice assistant for elderly people who struggle with technology. They can send messages, make calls, and stay connected just by talking."

**Demo 1 - Messaging (1 minute):**
- Say: "Send a message to Emma saying I'm thinking of you"
- Show: Backend logs confirm message sent
- Explain: No typing, no buttons, just natural speech

**Demo 2 - Video Call (1 minute):**
- Say: "Make a video call to John"
- Show: Call request created
- Explain: Hands-free calling for those with mobility issues

**Demo 3 - Incoming Call (1 minute):**
- Simulate incoming call
- Agent announces: "You have an incoming call from Sarah"
- Say: "Accept the call"
- Show: Call connected

**Closing (30 seconds):**
"This helps elderly people stay independent and connected with loved ones, reducing isolation and improving quality of life."

## 🎯 Key Points for Judges

1. **Solves Real Problem:** 1.4 million elderly people in UK suffer from chronic loneliness
2. **Accessible:** No need to learn new technology
3. **Scalable:** Built on modern, production-ready frameworks
4. **Extensible:** Easy to add medication reminders, emergency features, etc.

## 📊 What You Built

- ✅ Real-time voice processing with Pipecat
- ✅ Natural language understanding with GPT-4
- ✅ WebSocket-based real-time communication
- ✅ RESTful API for messaging and calls
- ✅ Modular, scalable architecture
- ✅ Production-ready code structure

## 🚀 Next Steps After Hackathon

1. Add user authentication
2. Integrate with existing messaging apps (WhatsApp, SMS)
3. Add contact management UI for caregivers
4. Implement persistent database
5. Deploy to cloud (AWS, Azure, or GCP)
6. Add health monitoring features
7. Create mobile app for caregivers

Good luck! 🍀
