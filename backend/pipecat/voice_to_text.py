import os
from dotenv import load_dotenv
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import (
    PipelineParams,
    PipelineWorker,
    ProcessorUnusablePolicy,
)
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.frameworks.langchain import LangchainProcessor

from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.workers.runner import WorkerRunner
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.transports.base_transport import BaseTransport
from backend.graph import compiled_graph
load_dotenv(override=True)




async def run_bot(
    transport: BaseTransport,
    runner_args: RunnerArguments,
):



    stt = DeepgramSTTService(
        api_key=os.environ["DEEPGRAM_API_KEY"],
    )



    tts = CartesiaTTSService(
        api_key=os.environ["CARTESIA_API_KEY"],
        settings=CartesiaTTSService.Settings(
            voice="86e30c1d-714b-4074-a1f2-1cb6b552fb49",
        ),
    )


    langgraph_processor = LangchainProcessor(
        chain=compiled_graph,
        transcript_key="input",
    )

 

    context = LLMContext()

    user_aggregator, assistant_aggregator = (
        LLMContextAggregatorPair(
            context,
            user_params=LLMUserAggregatorParams(
                vad_analyzer=SileroVADAnalyzer(),
            ),
        )
    )

 

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
        processor_unusable_policy=ProcessorUnusablePolicy.END,
    )

   

    runner = WorkerRunner(
        handle_sigint=runner_args.handle_sigint,
    )

    await runner.add_workers(worker)


    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):

        print("Client connected")

        # Initial instruction
        context.add_message(
            {
                "role": "developer",
                "content": (
                    "You are a hospital voice assistant. "
                    "Introduce yourself briefly and ask how "
                    "you can help the patient."
                ),
            }
        )

        # Trigger first LangGraph execution
        await worker.queue_frames(
            [LLMRunFrame()]
        )

  

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(
        transport,
        client,
    ):

        print("Client disconnected")

        await runner.cancel()

  

    await runner.run()

async def bot(runner_args: RunnerArguments):

    # create_transport() creates the transport based
    # on the runner configuration.
    transport = await create_transport(
        runner_args,
        transport_params,
    )

    await run_bot(
        transport,
        runner_args,
    )



if __name__ == "__main__":

    from pipecat.runner.run import main

    main()
