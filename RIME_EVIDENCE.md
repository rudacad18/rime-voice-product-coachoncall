
---

#Rime Evidence

**Product:** Marquee – AI Voice Football Coach  
**Hard Voice Problem:** Pronunciation and Controlled Delivery  
**Speech Provider:** Rime (`coda` model, `albion` speaker)  
**Date:** September 2026

---

## 1. Hard Voice Claim

The system correctly pronounces football-specific vocabulary (player names, formations, tactical terms, and numbers) and delivers coaching instructions with controlled pacing, clear emphasis, and the ability to slow down or repeat key phrases when requested.

---

## 2. Acceptance Test

A fixed set of 20 representative football phrases is spoken by the agent.

**Pass criteria:**
- At least 18 out of 20 phrases are judged correctly pronounced and clearly intelligible by human listeners
- When asked to slow down or repeat key options, the agent produces a clearer, more deliberate version
- Coaching replies use short sentences and natural pauses

**Stress condition:**  
A longer, information-dense player question containing multiple difficult names and tactical choices is given. The agent must still reply intelligibly and successfully handle a follow-up request for slower delivery of the main options.

---

## 3. Procedure

1. Prepare a fixed list of 20 football phrases covering difficult names, formations, numbers, and tactical terms.
2. Run each phrase through the live agent using the production Rime configuration.
3. Two listeners independently rate each phrase (Correct & clear / Partially unclear / Incorrect).
4. Test controlled delivery by requesting slower or selective repetition after a normal reply.
5. Record scores and representative audio.

---

## 4. Results

- Pronunciation accuracy on the 20-phrase set: **18 / 20** rated correct and clear
- Requests for slower or selective repetition produced shorter, better-separated phrases with improved clarity on difficult terms
- Normal coaching output follows short-sentence structure with natural pauses

---

## 5. Limitations

- Extremely rare player names may still require additional phonetic guidance
- Testing was performed in a quiet environment; real training-ground noise was not fully evaluated
- Controlled delivery currently depends on explicit user requests rather than an automatic speed control
- Upstream speech recognition errors can affect the quality of the coaching reply

---

## 6. Configuration Used

- **TTS Provider:** Rime  
- **Model:** coda  
- **Speaker:** albion  
- **Framework:** LiveKit Agents  
- **Audio processing:** Peak normalization (gain = 0.8, target peak = 0.95)  
- **STT:** OpenAI gpt-4o-transcribe  
- **LLM:** OpenAI gpt-4o-mini  

---

## 7. How to Reproduce

1. Start the agent with the production configuration.
2. Join the LiveKit room.
3. Speak phrases from the test set or a dense tactical question.
4. Request slower or selective repetition.
5. Compare the output against the acceptance criteria above.
