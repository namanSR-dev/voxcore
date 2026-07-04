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
        """
        Initializes the gateway with a reference to the core execution pipeline.
        
        Args:
            pipeline (RuntimeExecutionPipeline): The main execution engine of the system.
        """
        pass

    async def submit_request(self, request: Request) -> Response:
        """
        Submits a mapped Request to the runtime pipeline for execution.
        
        Args:
            request (Request): The domain Request entity containing user input.
            
        Returns:
            Response: The resulting domain Response entity from the AI.
            
        Raises:
            Exception: Any unhandled domain exception thrown by the runtime.
        """
        pass
