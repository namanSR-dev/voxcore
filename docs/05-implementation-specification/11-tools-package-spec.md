# Tools Package Implementation Specification

## Package Path
`backend/voxcore/tools/`

## Folder Structure
```
tools/
├── __init__.py
├── definitions/
│   ├── __init__.py
│   └── internal_tools.py
├── execution/
│   ├── __init__.py
│   └── tool_executor.py
├── lifecycle/
│   ├── __init__.py
│   └── tool_manager.py
├── registry/
│   ├── __init__.py
│   └── tool_registry.py
└── sandbox/
    ├── __init__.py
    └── execution_sandbox.py
```

---

## Files

### `tools/registry/tool_registry.py`

**Purpose**: Maintains a centralized list of all available executable tools and their schemas.
**Public Class**: `ToolRegistry`
**Abstract Interfaces**: None
**Constructor**: `__init__(self)`
**Public Methods**:
- `def register(self, tool: Any) -> None` (Internal API)
- `def get_tool(self, tool_name: str) -> Any` (Internal API)
- `def get_all_schemas(self) -> list[dict]` (Internal API)
**Return Types**: `None`, `Any`, `list`
**Expected Exceptions**: `ToolNotFoundError`
**Private Methods**: None
**Synchronous/Asynchronous**: Synchronous

```python
"""
tools/registry/tool_registry.py

Holds references to all registered tools (both internal and plugin-provided).
"""
from typing import Any, List, Dict

class ToolRegistry:
    """
    Central ledger mapping tool names to their implementations and schemas.
    """
    def __init__(self) -> None:
        pass

    def register(self, tool: Any) -> None:
        """
        Adds a new tool to the registry.
        """
        pass

    def get_tool(self, tool_name: str) -> Any:
        """
        Retrieves a tool instance by its name.
        """
        pass

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Retrieves the JSON schemas for all registered tools to inject into the LLM context.
        """
        pass
```

---

### `tools/execution/tool_executor.py`

**Purpose**: Safely invokes a tool implementation using provided arguments, handling timeouts and formatting.
**Public Class**: `ToolExecutor`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, sandbox: ExecutionSandbox)`
**Public Methods**:
- `async execute(self, tool: Any, arguments: dict) -> dict` (Internal API)
**Return Types**: `dict`
**Expected Exceptions**: `ToolExecutionError`
**Private Methods**: `_format_error`
**Synchronous/Asynchronous**: Asynchronous

```python
"""
tools/execution/tool_executor.py

Coordinates the safe execution of a tool.
"""
from typing import Dict, Any
from voxcore.tools.sandbox.execution_sandbox import ExecutionSandbox

class ToolExecutor:
    """
    Executes a requested tool, catching exceptions and enforcing timeouts.
    """
    def __init__(self, sandbox: ExecutionSandbox) -> None:
        pass

    async def execute(self, tool: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the tool inside the sandbox and returns the serialized result.
        """
        pass

    def _format_error(self, error: Exception) -> Dict[str, Any]:
        pass
```

---

### `tools/sandbox/execution_sandbox.py`

**Purpose**: Wraps tool execution in a protective boundary to prevent a failing tool from crashing the kernel.
**Public Class**: `ExecutionSandbox`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, timeout_seconds: int)`
**Public Methods**:
- `async run_safely(self, func: Any, *args, **kwargs) -> Any` (Internal API)
**Return Types**: `Any`
**Expected Exceptions**: `TimeoutError`
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
"""
tools/sandbox/execution_sandbox.py

Provides fault isolation for tool execution.
"""
from typing import Any, Callable

class ExecutionSandbox:
    """
    Ensures that a third-party tool cannot stall the event loop or crash the system.
    """
    def __init__(self, timeout_seconds: int) -> None:
        pass

    async def run_safely(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Executes the callable with strict timeout limits and exception boundaries.
        """
        pass
```

---

### `tools/lifecycle/tool_manager.py`

**Purpose**: The primary facade for the Tools package, exposing capabilities to the Runtime.
**Public Class**: `ToolManager`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, registry: ToolRegistry, executor: ToolExecutor)`
**Public Methods**:
- `def get_available_tools(self) -> list[dict]` (Public API)
- `async invoke_tool(self, name: str, arguments: dict) -> dict` (Public API)
**Return Types**: `list`, `dict`
**Expected Exceptions**: `Exception`
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
"""
tools/lifecycle/tool_manager.py

Orchestrates tool discovery and execution for the Runtime package.
"""
from typing import Dict, Any, List
from voxcore.tools.registry.tool_registry import ToolRegistry
from voxcore.tools.execution.tool_executor import ToolExecutor

class ToolManager:
    """
    The main service facade for interacting with the Tools subsystem.
    """
    def __init__(self, registry: ToolRegistry, executor: ToolExecutor) -> None:
        pass

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Returns the JSON schemas for all tools to be included in the LLM prompt.
        """
        pass

    async def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Looks up a tool by name and executes it safely.
        """
        pass
```
