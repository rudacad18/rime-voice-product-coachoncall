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


def _apply_gain(pcm_bytes: bytes, gain: float) -> bytes:
    """Scale 16-bit PCM audio by `gain`, with a soft ceiling instead of hard clipping.

    Vectorized with NumPy so it can keep up with real-time audio generation —
    a per-sample Python loop is slow enough to fall behind, which causes the
    pipeline to force-flush mid-segment and sounds like audio glitching/
    distorting partway through a sentence.
    """
    samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
    scaled = samples * gain

    # Soft-clip anything near/over full scale instead of hard-clamping, so
    # loud peaks round off smoothly rather than crackling.
    ceiling = 32767.0
    scaled = np.where(
        np.abs(scaled) > ceiling,
        np.sign(scaled) * ceiling * np.tanh(np.abs(scaled) / ceiling),
        scaled,
    )

    return scaled.astype(np.int16).tobytes()


class VolumeChunkedStream(tts.ChunkedStream):
    """Wraps another TTS's ChunkedStream and scales sample amplitude by `gain`."""

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
        request_id = utils.shortuuid()
        output_emitter.initialize(
            request_id=request_id,
            sample_rate=self._tts.sample_rate,
            num_channels=self._tts.num_channels,
            mime_type="audio/pcm",
        )

        async with self._wrapped_tts.synthesize(
            self._input_text, conn_options=self._conn_options
        ) as stream:
            async for audio in stream:
                frame = audio.frame
                output_emitter.push(_apply_gain(frame.data, self._gain))


class VolumeTTS(tts.TTS):
    def __init__(self, tts_engine: tts.TTS, gain: float = 0.5):
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
        return VolumeChunkedStream(
            tts_instance=self,
            input_text=text,
            conn_options=conn_options,
            gain=self._gain,
        )

    def prewarm(self) -> None:
        self._tts_engine.prewarm()

    async def aclose(self) -> None:
        await self._tts_engine.aclose()


class Assistant(Agent):
    def __init__(self):
        super().__init__(instructions=SYSTEM_PROMPT)


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    await ctx.wait_for_participant()

    session = AgentSession(
        stt=openai.STT(model="gpt-4o-transcribe"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=VolumeTTS(rime.TTS(model="coda", speaker="albion")),
        vad=ctx.proc.userdata["vad"],
        turn_detection=MultilingualModel(),
    )
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await session.say(INTRO_MESSAGE, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )