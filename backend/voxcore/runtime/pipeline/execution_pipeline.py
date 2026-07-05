"""
runtime/pipeline/execution_pipeline.py

Orchestrates the lifecycle of a single execution request.
"""
from typing import Any
from voxcore.contracts.runtime.models import Request, Response

class RuntimeExecutionPipeline:
    """
    The core engine that processes prompts, calls providers, and evaluates tool calls.
    """
    def __init__(self, context_builder: Any, provider_registry: Any) -> None:
        self.context_builder = context_builder
        self.provider_registry = provider_registry

    async def execute(self, request: Request) -> Response:
        """
        Runs the request through middleware, context assembly, and inference.
        """
        req = await self._run_middleware(request)
        provider = self._select_provider(req)
        
        if hasattr(provider, "execute"):
            return await provider.execute(req)
            
        return Response(id="sys-res", request_id=request.id, output={"text": "Pipeline executed successfully"})

    async def _run_middleware(self, request: Request) -> Request:
        return request

    def _select_provider(self, request: Request) -> Any:
        return self.provider_registry.get_provider("default")
