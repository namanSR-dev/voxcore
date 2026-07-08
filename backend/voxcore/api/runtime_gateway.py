"""
api/runtime_gateway.py

Provides a single abstraction boundary for invoking the backend runtime.
"""
from voxcore.contracts.runtime.models import Request, Response
from voxcore.runtime.pipeline.execution_pipeline import RuntimeExecutionPipeline

class RuntimeGateway:
    """
    Defines the strict boundary through which the API package hands work to the runtime.
    """
    def __init__(self, pipeline: RuntimeExecutionPipeline) -> None:
        self.pipeline = pipeline

    async def submit_request(self, request: Request) -> Response:
        return await self.pipeline.execute(request)

    async def submit_request_stream(self, request: Request):
        """
        Submits a request and yields the generated sentences sequentially.
        """
        async for sentence in self.pipeline.execute_stream(request):
            yield sentence
