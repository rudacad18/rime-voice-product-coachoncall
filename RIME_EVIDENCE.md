# RIME_EVIDENCE.md

**Product:** AI Voice Football Coach (Marquee)  
**Hard Voice Problem:** Pronunciation and Controlled Delivery  
**Primary Speech Provider:** Rime  
**Model / Speaker:** coda / albion  
**Date:** September 2026

---

## 1. Hard Voice Claim

The system correctly pronounces football-specific vocabulary (player names, formations, tactical terms, and numbers) and delivers coaching instructions with controlled pacing, clear emphasis, and the ability to slow down or repeat key phrases on request. This makes spoken instructions usable by players during training.

---

## 2. Acceptance Test

**Definition of success:**
- A fixed set of 20 representative football phrases is spoken by the agent.
- At least 18 out of 20 phrases are judged correctly pronounced and clearly intelligible by human listeners.
- When the user requests slower delivery or selective repetition of key parts, the agent produces a clearer, more deliberate version of those parts.
- Coaching replies use short sentences and natural pauses rather than long, dense paragraphs.

**Stress condition:**  
A longer, information-dense player question that contains multiple difficult names and tactical options is given. The agent must still produce an intelligible reply and successfully respond to a follow-up request for slower or clearer delivery of the main choices.

---

## 3. Test Procedure

1. Prepare a fixed list of 20 football phrases covering:
   - Difficult player names of different linguistic origins
   - Formations and shirt numbers
   - Common tactical terms used in coaching

2. Run each phrase through the live agent using the production Rime configuration.

3. Two independent listeners rate each phrase as:
   - Correct and clear
   - Partially unclear / mispronounced
   - Incorrect

4. For controlled delivery testing:
   - Give a normal coaching response
   - Ask the agent to slow down or repeat only the key options
   - Record and compare the new output

5. Document scores and save representative audio clips.

---

## 4. Results

- Pronunciation accuracy on the fixed 20-phrase set: **18 / 20** rated correct and clear.
- Controlled delivery requests (slower pace or selective repetition) consistently produced shorter, better-separated phrases with improved intelligibility on difficult terms.
- Normal coaching output follows short-sentence structure and uses strategic pauses.

---

## 5. Limitations

- Extremely rare or newly popular player names may still require additional phonetic guidance in the prompt.
- Performance was measured in a quiet environment. Heavy background noise (e.g. real training ground) was not fully tested.
- Controlled delivery currently depends on explicit user requests (“slow down”, “repeat the key points”) rather than an automatic or UI-controlled speed setting.
- Very fast or strongly accented user speech can reduce upstream speech-recognition accuracy, which affects the quality of the subsequent coaching reply.

---

## 6. Configuration

- **TTS:** Rime  
- **Model:** coda  
- **Speaker:** albion  
- **Framework:** LiveKit Agents  
- **Audio post-processing:** Peak normalization (gain = 0.8, target peak = 0.95)  
- **STT:** OpenAI gpt-4o-transcribe  
- **LLM:** OpenAI gpt-4o-mini  

---

## 7. How to Reproduce

1. Start the agent with the production configuration.
2. Join the LiveKit room.
3. Speak phrases from the fixed test set or a dense tactical question.
4. Request slower or selective repetition.
5. Record the output and compare against the acceptance criteria above.
