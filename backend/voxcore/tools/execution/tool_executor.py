"""
tools/execution/tool_executor.py

Coordinates the safe execution of a tool.
"""
from typing import Dict, Any
from voxcore.tools.sandbox.execution_sandbox import ExecutionSandbox
from voxcore.contracts.tools.i_tool import ITool

class ToolExecutor:
    """
    Executes a requested tool, catching exceptions and enforcing timeouts.
    """
    def __init__(self, sandbox: ExecutionSandbox) -> None:
        self.sandbox = sandbox

    async def execute(self, tool: ITool, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the tool inside the sandbox and returns the serialized result.
        """
        try:
            result = await self.sandbox.run_safely(tool.execute, arguments)
            return {"status": "success", "data": result}
        except Exception as e:
            return self._format_error(e)

    def _format_error(self, error: Exception) -> Dict[str, Any]:
        return {"status": "error", "message": str(error)}
