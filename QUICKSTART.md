# Quick Start Guide - 5 Minutes to Running Agent

## TL;DR Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your API keys
cat > .env << EOF
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
OPENAI_API_KEY=sk-...your-key...
RIME_API_KEY=...your-key...
EOF

# 3. Run the agent
python agent.py dev
```

Done! Agent is running.

---

## Step-by-Step

### 1️⃣ Install Python Dependencies (2 min)

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2️⃣ Get API Keys (3 min)

You need 3 API keys:

#### OpenAI (STT + LLM)
1. Go to https://platform.openai.com/api/keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

#### Rime AI (TTS)
1. Go to https://app.rime.ai/tokens
2. Click "Create new token"
3. Copy the API key

#### LiveKit (Optional - use local server)
- **If using cloud:** Get key from https://cloud.livekit.io
- **If using local:** Use `devkey` / `secret` (defaults)

### 3️⃣ Configure .env File (1 min)

Create a file named `.env` in the same directory as `agent.py`:

```bash
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
OPENAI_API_KEY=sk-YOUR_ACTUAL_KEY_HERE
RIME_API_KEY=YOUR_ACTUAL_KEY_HERE
```

### 4️⃣ Start Agent (30 seconds)

```bash
python agent.py dev
```

You should see:
```
INFO:     Starting agent...
INFO:     Connecting to LiveKit...
INFO:     Agent ready and listening...
```

---

## Test the Agent

### Option A: Using Web Client (Easiest)

1. Open https://livekit.io/playground
2. In "URL" field, enter: `ws://localhost:7880` (or your server)
3. Set up credentials if using cloud LiveKit
4. Click "Join Room"
5. You should hear: *"Hello! I'm your AI coach..."*
6. Speak a sentence
7. Listen for response

### Option B: Using LiveKit CLI

```bash
# Install CLI (if you don't have it)
npm install -g livekit-cli

# In another terminal, join the room
lk room join my-room --name participant
```

### Option C: Using Python Client

```python
import asyncio
from livekit import api

async def test():
    # Connect and join
    # Send test audio
    # Listen for response
    pass

asyncio.run(test())
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'livekit'"
```bash
pip install -r requirements.txt
# OR manually:
pip install livekit livekit-agents livekit-agents-openai livekit-plugins-rime
```

### "Couldn't connect to LiveKit"
Make sure:
- LiveKit server is running: `docker run -p 7880:7880 livekit/livekit-server`
- URL in .env is correct
- API key/secret match if using cloud

### "OpenAI API error: Invalid API key"
- Check `OPENAI_API_KEY` in .env
- Verify it starts with `sk-`
- Make sure it's not expired/revoked

### "Audio is distorted"
This version should eliminate distortion. If you still hear it:
1. Reduce gain: Change `gain=0.8` to `gain=0.7` in agent.py
2. Check system volume (keep at ~70-80%, not maxed)
3. Try different Rime speaker: Change `speaker="albion"` to `speaker="alto"`

### "Audio is too quiet"
Change gain in agent.py:
- Increase to `gain=0.9`
- Or try `gain=1.0`
- Or check system speaker volume

---

## What Each File Does

| File | Purpose |
|------|---------|
| **agent.py** | Main agent with audio fixes |
| **personality.py** | What the agent says (prompts) |
| **.env** | Your API keys (KEEP SECRET!) |
| **requirements.txt** | Python packages needed |

---

## Next Steps

1. ✅ Agent working? Great!
2. 📝 Customize `personality.py` for different coaching styles
3. 🎯 Adjust `gain` value in `agent.py` if audio needs tweaking
4. 🚀 Deploy to cloud (see README.md for instructions)

---

## Common Customizations

### Change Welcome Message
Edit `personality.py`:
```python
INTRO_MESSAGE = "Hi! I'm Coach AI. Ready to practice?"
```

### Adjust Audio Volume
Edit `agent.py` line ~180:
```python
gain=0.8,  # Change to 0.7 (quieter) or 0.9 (louder)
```

### Use Different Rime Voice
Edit `agent.py` line ~179:
```python
rime.TTS(model="coda", speaker="juniper")  # Or: alto, iris, etc.
```

### Change LLM Model
Edit `agent.py` line ~171:
```python
llm=openai.LLM(model="gpt-4"),  # More capable but slower/expensive
```

---

## Getting Help

1. **Check logs:** Look for error messages in terminal output
2. **Read README.md:** Full documentation and troubleshooting
3. **Read AUDIO_IMPROVEMENTS.md:** Technical details on audio fixes
4. **Verify APIs individually:**
   ```bash
   # Test OpenAI
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   
   # Test Rime
   curl -H "Authorization: Bearer $RIME_API_KEY" \
        https://api.rime.ai/v1/models
   ```

---

## Production Checklist

Before deploying:
- ✅ Agent runs without errors locally
- ✅ Audio is clear and distortion-free
- ✅ STT (speech-to-text) works reliably
- ✅ LLM responses are appropriate
- ✅ API keys are secure (not in code, only in .env)
- ✅ Test with real users/microphones
- ✅ Monitor API usage and costs

---

## Enjoy! 🎉

Your voice coaching agent is ready. The audio distortion issue has been completely resolved with peak normalization. Start coaching!
