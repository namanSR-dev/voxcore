"""
tools/sandbox/execution_sandbox.py

Provides fault isolation for tool execution.
"""
from typing import Any, Callable
import asyncio

class ExecutionSandbox:
    """
    Ensures that a third-party tool cannot stall the event loop or crash the system.
    """
    def __init__(self, timeout_seconds: int = 5) -> None:
        self.timeout_seconds = timeout_seconds

    async def run_safely(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Executes the callable with strict timeout limits and exception boundaries.
        """
        try:
            if asyncio.iscoroutinefunction(func):
                return await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout_seconds)
            else:
                # Run sync functions in a threadpool to avoid blocking the event loop
                loop = asyncio.get_running_loop()
                future = loop.run_in_executor(None, lambda: func(*args, **kwargs))
                return await asyncio.wait_for(future, timeout=self.timeout_seconds)
        except asyncio.TimeoutError:
            raise Exception(f"Tool execution timed out after {self.timeout_seconds} seconds")
        except Exception as e:
            raise Exception(f"Tool execution crashed: {e}")
