# Marquee – AI Voice Football Coach

Marquee is a hands-free AI football coach that players can talk to during training.  
It uses **Rime** as the primary text-to-speech engine and focuses on solving **pronunciation and controlled delivery** of football-specific language.

## Hard Voice Problem

**Pronunciation and Controlled Delivery**

Football coaching language contains difficult player names, formations, numbers, and tactical terms. Most TTS systems mispronounce them or deliver instructions in long, hard-to-follow sentences.  

Marquee is designed so that:
- Difficult names and tactical terms are pronounced clearly
- Instructions use short sentences and natural pauses
- The coach can slow down or repeat key points on request

## Who It’s For

Amateur and grassroots football players who train without a coach present and need clear spoken guidance while their hands and eyes are busy.

## How It Works

1. Player speaks a question or describes a situation
2. Speech is transcribed (OpenAI)
3. The coaching reply is generated (OpenAI)
4. Rime speaks the reply with controlled pacing and clear pronunciation
5. Player can ask the coach to slow down or repeat key parts

## Tech Stack

- **TTS**: Rime (`coda` model, `albion` speaker)
- **STT**: OpenAI `gpt-4o-transcribe`
- **LLM**: OpenAI `gpt-4o-mini`
- **Realtime framework**: LiveKit Agents
- **Audio processing**: Peak normalization (gain = 0.8) to avoid distortion
- **VAD & Turn detection**: Silero + Multilingual turn detector

## Quick Start


# 1. Clone the repo
git clone https://github.com/rudacad18/rime-voice-product-coachoncall.git
cd rime-voice-product-coachoncall

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Add your keys:
# LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
# OPENAI_API_KEY, RIME_API_KEY

# 5. Run the agent
python agent.py dev
Then join the room using the LiveKit Playground or your own client.
Project Structure
textagent.py              # Main LiveKit agent + Rime TTS + audio gain
personality.py        # Football coach system prompt and intro
RIME_EVIDENCE.md      # Evidence for the hard voice claim
README.md             # This file
.env.example          # Environment template
Rime Configuration

Provider: Rime
Model: coda
Speaker: albion
Role: Primary and only spoken output of the coach

##Limitations

Very rare or newly popular player names may still need extra phonetic hints
Performance in loud outdoor training environments has not been fully tested
Controlled delivery currently relies on the user asking to “slow down” or “repeat”
Heavy accents or very fast speech can reduce transcription quality

*AI Assistance Disclosure*
Significant portions of the code, prompts, and documentation were developed with the help of AI coding assistants. All components have been reviewed and tested by the author.
**Licence**
This project is for the DataForge × Rime Hackathon.
