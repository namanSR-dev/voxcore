# Contracts Package Implementation Specification

## Package Path
`backend/voxcore/contracts/`

## Folder Structure
```
contracts/
├── __init__.py
├── common/
│   ├── __init__.py
│   ├── enums.py
│   └── errors.py
├── configuration/
│   ├── __init__.py
│   └── i_configuration.py
├── events/
│   ├── __init__.py
│   ├── i_event.py
│   └── i_event_subscriber.py
├── memory/
│   ├── __init__.py
│   └── i_memory_store.py
├── plugins/
│   ├── __init__.py
│   ├── i_plugin.py
│   └── i_plugin_manifest.py
├── providers/
│   ├── __init__.py
│   ├── i_provider.py
│   └── i_provider_factory.py
├── runtime/
│   ├── __init__.py
│   └── models.py
├── security/
│   ├── __init__.py
│   └── i_authorizer.py
├── services/
│   ├── __init__.py
│   ├── i_conversation_service.py
│   └── i_validation_service.py
└── tools/
    ├── __init__.py
    └── i_tool.py
```

---

## Files

### `contracts/providers/i_provider.py`

**Purpose**: Defines the abstract boundary for external AI execution targets.
**Public Class**: `IProvider` (Protocol/ABC)
**Abstract Interfaces**: None
**Constructor**: None (Abstract)
**Public Methods**:
- `async generate_response(self, context: Any) -> Any` (Public API)
- `async generate_embeddings(self, text: str) -> list[float]` (Public API)
**Return Types**: Generic/Any
**Expected Exceptions**: `NotImplementedError`
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
"""
contracts/providers/i_provider.py

Defines the standard interface that all AI model providers must implement.
"""
from typing import Any, List
from abc import ABC, abstractmethod

class IProvider(ABC):
    """
    Abstract interface for executing prompts against an external model.
    """
    
    @abstractmethod
    async def generate_response(self, context: Any) -> Any:
        """
        Submits the assembled context to the provider for inference.
        """
        pass

    @abstractmethod
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Requests vector embeddings for the provided text.
        """
        pass
```

---

### `contracts/services/i_conversation_service.py`

**Purpose**: Defines the abstract contract for conversation management logic.
**Public Class**: `IConversationService` (Protocol/ABC)
**Abstract Interfaces**: None
**Constructor**: None
**Public Methods**:
- `async process_turn(self, session_id: str, utterance: str) -> str` (Public API)
**Return Types**: `str`
**Expected Exceptions**: `NotImplementedError`
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
"""
contracts/services/i_conversation_service.py

Defines the contract for managing conversation state and turns.
"""
from abc import ABC, abstractmethod

class IConversationService(ABC):
    """
    Abstract interface for handling conversational logic independent of transport.
    """
    
    @abstractmethod
    async def process_turn(self, session_id: str, utterance: str) -> str:
        """
        Processes a single conversational turn.
        """
        pass
```

---

### `contracts/runtime/models.py`

**Purpose**: Defines pure data structures (DTOs/Records) shared universally across packages.
**Public Class**: `Request`, `Response`, `ExecutionContext` (Dataclasses)
**Abstract Interfaces**: None
**Constructor**: Dataclass implicit `__init__`
**Public Methods**: None (Data bags only)
**Return Types**: N/A
**Expected Exceptions**: None
**Private Methods**: None
**Synchronous/Asynchronous**: N/A

```python
"""
contracts/runtime/models.py

Pure data structures representing the core domain entities exchanged between packages.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class Request:
    """
    Immutable representation of an inbound user prompt or action request.
    """
    id: str
    session_id: str
    payload: Dict[str, Any]

@dataclass(frozen=True)
class Response:
    """
    Immutable representation of the system's generated output.
    """
    id: str
    request_id: str
    output: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
```

---

### `contracts/plugins/i_plugin.py`

**Purpose**: Defines the lifecycle hooks that third-party extensions must implement.
**Public Class**: `IPlugin` (Protocol/ABC)
**Abstract Interfaces**: None
**Constructor**: None
**Public Methods**:
- `def activate(self, registry: Any) -> None` (Public API)
- `def deactivate(self) -> None` (Public API)
**Return Types**: `None`
**Expected Exceptions**: `NotImplementedError`
**Private Methods**: None
**Synchronous/Asynchronous**: Synchronous

```python
"""
contracts/plugins/i_plugin.py

Defines the lifecycle interface for external platform extensions.
"""
from typing import Any
from abc import ABC, abstractmethod

class IPlugin(ABC):
    """
    Abstract interface for VoxCore plugins to contribute capabilities.
    """
    
    @abstractmethod
    def activate(self, registry: Any) -> None:
        """
        Invoked when the plugin is booted. The plugin should register its tools or providers here.
        """
        pass

    @abstractmethod
    def deactivate(self) -> None:
        """
        Invoked during shutdown to allow the plugin to clean up resources.
        """
        pass
```

---

### `contracts/tools/i_tool.py`

**Purpose**: Defines the execution boundary for safe function calling by the LLM.
**Public Class**: `ITool` (Protocol/ABC)
**Abstract Interfaces**: None
**Constructor**: None
**Public Methods**:
- `def get_schema(self) -> dict` (Public API)
- `async execute(self, arguments: dict) -> dict` (Public API)
**Return Types**: `dict`
**Expected Exceptions**: `NotImplementedError`
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
"""
contracts/tools/i_tool.py

Defines the contract for LLM-callable functions.
"""
from typing import Dict, Any
from abc import ABC, abstractmethod

class ITool(ABC):
    """
    Abstract interface for executable actions.
    """
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Returns the JSON Schema describing this tool's arguments.
        """
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the tool logic with the provided arguments.
        """
        pass
```
