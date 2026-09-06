# Marquee — Voice Football Coach

A real-time voice agent that coaches you on football tactics, training design,
and match analysis. Built for the DataForge × Rime hackathon.

## Why voice

Marquee is a full-duplex voice coach. You talk, it listens, reasons, and
answers out loud through Rime TTS. Removing speech would break the product —
there's no chat fallback, no text transcript to read. The spoken delivery is
the interface.

## Hard voice problem: pronunciation and controlled delivery

Football is full of names, formations, and jargon — "false nine", "tiki-taka",
player names, set-piece codes. The agent must pronounce them correctly and
deliver coaching cues at a controlled pace.

**Acceptance test (defined before demo):**
- Render the same coaching turn with two text variants (one with phonetic
  hints, one without) using the identical Rime model and speaker.
- Save both audio clips.
- A listener rates intelligibility of names and jargon on a 1–5 scale.
- Pass = average ≥ 4, with no name mispronounced in the hinted variant.

## Architecture
User mic ──► LiveKit (WebRTC) ──► Agent
│
STT: gpt-4o-transcribe
LLM: gpt-4o-mini
TTS: Rime (coda / cupola)  ◄── primary spoken output
VAD: Silero + turn detector
Noise cancellation: Krisp


- `agent.py` — LiveKit Agents entrypoint, VolumeTTS wrapper, session setup
- `personality.py` — system prompt for the "Marquee" coach persona
- `token_server.py` — issues short-lived LiveKit room tokens for the frontend

## Rime configuration (shipped path)

| Setting | Value |
|---|---|
| Model ID | `coda` |
| Speaker | `cupola` |
| Language | `eng` |
| Endpoint | Rime default (US) |
| Audio format | PCM, streamed |
| Transport | LiveKit WebRTC |

## Setup


# 1. Clone and enter
git clone https://github.com/rudacad18/rime-voice-product-coachoncall.git
cd rime-voice-product-coachoncall

# 2. Create your secret file (never commit this)
cp .env.example .env
# fill in: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET,
#          OPENAI_API_KEY, RIME_API_KEY

# 3. Install and download model files
uv sync
uv run python agent.py download-files

# 4. Run the agent
uv run python agent.py dev

# 5. (optional) run the token server for the custom frontend
uv run python token_server.py 

Open the LiveKit Agents Playground or coachoncall.lovable.app to talk.
