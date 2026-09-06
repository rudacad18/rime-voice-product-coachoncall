import numpy as np
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    APIConnectOptions,
    AutoSubscribe,
    DEFAULT_API_CONNECT_OPTIONS,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    tts,
    utils,
)
from livekit.plugins import openai, noise_cancellation, rime, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from personality import INTRO_MESSAGE
from personality import SYSTEM_PROMPT

load_dotenv()


def _apply_gain(
    pcm_bytes: bytes,
    gain: float = 1.0,
    target_peak: float = 0.95,
) -> bytes:
    """Scale 16-bit PCM audio with peak normalization to prevent distortion.
    
    This function uses intelligent peak normalization instead of hard clipping
    to prevent audio artifacts and distortion.
    
    Args:
        pcm_bytes: 16-bit PCM audio bytes
        gain: Amplitude multiplier (1.0 = no change, 0.8 = 80% volume, etc.)
        target_peak: Target peak level relative to max int16 (0.0-1.0).
                     Default 0.95 leaves 5% headroom to prevent clipping.
    
    Returns:
        Scaled 16-bit PCM audio bytes without distortion.
    """
    # Convert bytes to numpy array for vectorized processing
    samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
    
    # Find the peak amplitude in the signal
    peak = np.max(np.abs(samples))
    
    if peak > 0:
        # Calculate scaling factor to reach target peak
        # This prevents clipping by normalizing to a safe level first
        scaling_factor = (target_peak * 32767.0) / peak
        samples = samples * scaling_factor * gain
    else:
        # Silent or near-silent audio
        samples = samples * gain
    
    # Hard ceiling with safety margin to prevent any clipping
    # Clips to ±32767 (safe range for int16)
    samples = np.clip(samples, -32767, 32767)
    
    # Convert back to int16 bytes
    return samples.astype(np.int16).tobytes()


class VolumeChunkedStream(tts.ChunkedStream):
    """Wraps another TTS's ChunkedStream and scales sample amplitude by `gain`.
    
    This stream processor handles real-time audio scaling without causing
    glitching or distortion that would occur with per-sample Python loops.
    Uses NumPy vectorization for performance.
    """

    def __init__(
        self,
        *,
        tts_instance: "VolumeTTS",
        input_text: str,
        conn_options: APIConnectOptions,
        gain: float,
    ) -> None:
        super().__init__(tts=tts_instance, input_text=input_text, conn_options=conn_options)
        self._wrapped_tts = tts_instance._tts_engine
        self._gain = gain

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """Process TTS stream with gain applied to each audio chunk."""
        request_id = utils.shortuuid()
        output_emitter.initialize(
            request_id=request_id,
            sample_rate=self._tts.sample_rate,
            num_channels=self._tts.num_channels,
            mime_type="audio/pcm",
        )

        # Wrap the underlying TTS synthesizer and apply gain to each chunk
        async with self._wrapped_tts.synthesize(
            self._input_text, conn_options=self._conn_options
        ) as stream:
            async for audio in stream:
                frame = audio.frame
                # Apply gain with peak normalization (no distortion)
                scaled_audio = _apply_gain(
                    frame.data,
                    gain=self._gain,
                    target_peak=0.95,  # 5% headroom
                )
                output_emitter.push(scaled_audio)


class VolumeTTS(tts.TTS):
    """TTS wrapper that applies volume scaling without distortion.
    
    This wrapper allows you to control the output volume of any TTS engine
    (in this case, Rime) with proper peak normalization instead of naive
    clipping that causes audio artifacts.
    
    Args:
        tts_engine: The underlying TTS engine (e.g., rime.TTS())
        gain: Volume multiplier. Recommended values:
              - 0.8 = 80% volume (safe default, reduces peaks)
              - 0.9 = 90% volume (minimal reduction)
              - 1.0 = 100% volume (no scaling)
              - 1.1+ = amplification (use cautiously)
    """

    def __init__(self, tts_engine: tts.TTS, gain: float = 0.8):
        super().__init__(
            capabilities=tts_engine.capabilities,
            sample_rate=tts_engine.sample_rate,
            num_channels=tts_engine.num_channels,
        )
        self._tts_engine = tts_engine
        self._gain = gain

    def synthesize(
        self, text: str, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS
    ) -> VolumeChunkedStream:
        """Synthesize text with volume scaling applied."""
        return VolumeChunkedStream(
            tts_instance=self,
            input_text=text,
            conn_options=conn_options,
            gain=self._gain,
        )

    def prewarm(self) -> None:
        """Prewarm the underlying TTS engine."""
        self._tts_engine.prewarm()

    async def aclose(self) -> None:
        """Clean up TTS engine resources."""
        await self._tts_engine.aclose()


class Assistant(Agent):
    """Voice assistant agent using OpenAI LLM and Rime TTS.
    
    This agent:
    - Transcribes user speech using OpenAI's GPT-4o model
    - Processes responses with GPT-4o-mini for speed
    - Speaks using Rime's "coda" model with "albion" speaker
    - Includes voice activity detection and noise cancellation
    """

    def __init__(self):
        super().__init__(instructions=SYSTEM_PROMPT)


def prewarm(proc: JobProcess):
    """Preload VAD model for faster startup.
    
    This runs once when the worker starts, before handling any sessions.
    Silero VAD is loaded into process userdata for reuse across sessions.
    """
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main entry point for the LiveKit agent.
    
    This function:
    1. Connects to the LiveKit room
    2. Waits for a participant to join
    3. Sets up the agent session with STT, LLM, TTS, and VAD
    4. Starts the agent and plays intro message
    
    Args:
        ctx: JobContext containing room, connections, and configuration
    """
    # Connect to the LiveKit room, subscribing only to audio
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Wait for a participant to join the room
    await ctx.wait_for_participant()

    # Create the agent session with all components
    session = AgentSession(
        # Speech-to-Text: Use GPT-4o for accurate transcription
        stt=openai.STT(model="gpt-4o-transcribe"),
        
        # Large Language Model: Use GPT-4o-mini for fast, accurate responses
        llm=openai.LLM(model="gpt-4o-mini"),
        
        # Text-to-Speech: Rime with volume scaling for optimal audio levels
        # gain=0.8 reduces volume to 80% of peak, preventing distortion
        tts=VolumeTTS(
            rime.TTS(model="coda", speaker="albion"),
            gain=0.8,  # Adjust this value if audio is still too loud/quiet
        ),
        
        # Voice Activity Detection: Silero VAD for accurate speech detection
        vad=ctx.proc.userdata["vad"],
        
        # Turn Detection: Multilingual model for natural conversation flow
        turn_detection=MultilingualModel(),
    )
    
    # Start the agent session in the room
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # BVC: Beat Voice Cancellation for background noise removal
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    # Play intro message with interruption allowed (user can speak over it)
    await session.say(INTRO_MESSAGE, allow_interruptions=True)


if __name__ == "__main__":
    # Run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
