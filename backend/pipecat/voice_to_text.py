import os

from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.frameworks.langchain import LangchainProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.workers.runner import WorkerRunner

from backend.Graph.workflow import compiled_graph

load_dotenv(override=True)


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    """Build and run the STT -> LangGraph -> TTS voice pipeline."""

    # ---- Speech to text -------------------------------------------------
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    # ---- Text to speech -------------------------------------------------
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        settings=CartesiaTTSService.Settings(
            voice="86e30c1d-714b-4074-a1f2-1cb6b552fb49",
        ),
    )

    # ---- LangGraph in the middle ---------------------------------------
    # compiled_graph is a Runnable: {"input": <transcript>} -> <reply text>.
    langgraph_processor = LangchainProcessor(
        chain=compiled_graph,
        transcript_key="input",
    )

    # ---- Context aggregation + VAD -------------------------------------
    context = LLMContext()
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    # ---- Pipeline -------------------------------------------------------
    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            langgraph_processor,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )

    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        idle_timeout_secs=runner_args.pipeline_idle_timeout_secs,
    )

    runner = WorkerRunner(handle_sigint=runner_args.handle_sigint)
    await runner.add_workers(worker)

    @worker.rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        # Fired once the browser's RTVI data channel is ready, so the greeting
        # (and its transcript) reliably reaches the frontend chat.
        logger.info("Client ready - sending greeting")
        context.add_message(
            {
                "role": "developer",
                "content": (
                    "You are a hospital voice assistant. Introduce yourself "
                    "briefly and ask how you can help the patient."
                ),
            }
        )
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected")
        # Thread this caller's conversation so multi-turn booking has memory.
        # The processor forwards this as session_id -> our graph's thread_id.
        participant_id = (
            getattr(client, "id", None)
            or getattr(client, "participant_id", None)
            or "web-client"
        )
        langgraph_processor.set_participant_id(str(participant_id))

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await runner.cancel()

    await runner.run()


async def bot(runner_args: RunnerArguments):
    """Entry point used by the pipecat dev runner (pipecat.runner.run.main).

    transport_params maps a transport name to a factory producing its
    TransportParams. We enable the SmallWebRTC transport (browser <-> bot).
    """
    transport_params = {
        # The dev runner looks up the "webrtc" key for SmallWebRTC browser
        # clients.
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    }

    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
