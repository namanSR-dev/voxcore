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
        pass

    async def execute(self, request: Request) -> Response:
        """
        Runs the request through middleware, context assembly, and inference.
        """
        pass

    async def _run_middleware(self, request: Request) -> Request:
        pass

    def _select_provider(self, request: Request) -> Any:
        pass
