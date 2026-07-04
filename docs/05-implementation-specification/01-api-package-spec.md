# API Package Implementation Specification

## Package Path
`backend/voxcore/api/`

## Folder Structure
```
api/
├── __init__.py
├── adapters/
│   ├── __init__.py
│   ├── request_adapter.py
│   └── response_adapter.py
├── controllers/
│   ├── __init__.py
│   ├── http_controller.py
│   └── websocket_controller.py
├── validation/
│   ├── __init__.py
│   └── schema_validator.py
├── exception_translator.py
└── runtime_gateway.py
```

---

## Files

### `api/controllers/http_controller.py`

**Purpose**: Receives external REST requests, orchestrates validation and adaptation, and delegates to the runtime.
**Public Class**: `HttpController`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, gateway: RuntimeGateway, translator: ExceptionTranslator)`
**Public Methods**:
- `async accept_request(self, payload: dict) -> dict` (Public API)
- `async health_check(self) -> dict` (Public API)
**Return Types**: `dict`
**Expected Exceptions**: `ValueError`
**Private Methods**: `_extract_headers`
**Synchronous/Asynchronous**: Asynchronous

```python
"""
api/controllers/http_controller.py

Receives HTTP REST requests, orchestrates validation, delegates mapping to adapters, 
and hands off execution to the runtime gateway. Connects HTTP 4xx/5xx responses.
"""
from typing import Dict, Any
from voxcore.api.runtime_gateway import RuntimeGateway
from voxcore.api.exception_translator import ExceptionTranslator

class HttpController:
    """
    HTTP route handler that isolates transport concerns from the VoxCore runtime.
    """
    
    def __init__(self, gateway: RuntimeGateway, translator: ExceptionTranslator) -> None:
        """
        Initializes the HTTP Controller with its required collaborators.
        """
        pass

    async def accept_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts a conversational or execution prompt via HTTP.
        
        Args:
            payload: Raw JSON dictionary from the client.
            
        Returns:
            Dict representing the formatted Response JSON.
        """
        pass

    async def health_check(self) -> Dict[str, Any]:
        """
        Probes runtime status for load balancers.
        
        Returns:
            System status map.
        """
        pass

    def _extract_headers(self, raw_headers: Dict[str, str]) -> Dict[str, str]:
        """
        Extracts and normalizes relevant HTTP headers.
        """
        pass
```

---

### `api/controllers/websocket_controller.py`

**Purpose**: Manages long-lived socket connections for streaming audio or text, delegating events to the runtime.
**Public Class**: `WebSocketController`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, gateway: RuntimeGateway, translator: ExceptionTranslator)`
**Public Methods**:
- `async handle_connection(self, connection_id: str) -> None` (Public API)
**Return Types**: `None`
**Expected Exceptions**: `ConnectionError`
**Private Methods**: `_receive_loop`, `_send_loop`
**Synchronous/Asynchronous**: Asynchronous

```python
"""
api/controllers/websocket_controller.py

Manages long-lived bidirectional WebSocket connections for streaming responses.
"""
from voxcore.api.runtime_gateway import RuntimeGateway
from voxcore.api.exception_translator import ExceptionTranslator

class WebSocketController:
    """
    WebSocket route handler that manages connection state and streams messages to/from the runtime.
    """
    
    def __init__(self, gateway: RuntimeGateway, translator: ExceptionTranslator) -> None:
        """
        Initializes the WebSocket Controller.
        """
        pass

    async def handle_connection(self, connection_id: str) -> None:
        """
        Manages the lifecycle of a single WebSocket connection.
        
        Args:
            connection_id: Unique identifier for the socket connection.
        """
        pass

    async def _receive_loop(self) -> None:
        """
        Internal loop to listen for incoming socket messages.
        """
        pass

    async def _send_loop(self) -> None:
        """
        Internal loop to flush outgoing responses to the socket.
        """
        pass
```

---

### `api/validation/schema_validator.py`

**Purpose**: Asserts incoming transport payloads against expected schemas before entering the runtime.
**Public Class**: `SchemaValidator`
**Abstract Interfaces**: None
**Constructor**: `__init__(self)`
**Public Methods**:
- `def validate_request(self, payload: dict) -> bool` (Internal API)
**Return Types**: `bool`
**Expected Exceptions**: `ValueError`
**Private Methods**: None
**Synchronous/Asynchronous**: Synchronous

```python
"""
api/validation/schema_validator.py

Validates incoming JSON payloads to ensure they match expected constraints.
"""
from typing import Dict, Any

class SchemaValidator:
    """
    Enforces structural limits on inbound requests before they touch the runtime.
    """
    
    def __init__(self) -> None:
        """
        Initializes the schema validator.
        """
        pass

    def validate_request(self, payload: Dict[str, Any]) -> bool:
        """
        Asserts the payload schema is valid.
        
        Args:
            payload: Raw JSON dictionary.
            
        Returns:
            True if valid.
            
        Raises:
            ValueError if schema violation occurs.
        """
        pass
```

---

### `api/adapters/request_adapter.py`

**Purpose**: Maps external Data Transfer Objects (DTOs) into internal domain `Request` models.
**Public Class**: `RequestAdapter`
**Abstract Interfaces**: None
**Constructor**: `__init__(self)`
**Public Methods**:
- `def to_domain(self, payload: dict) -> Request` (Internal API)
**Return Types**: `Request` (from domain models)
**Expected Exceptions**: `KeyError`
**Private Methods**: None
**Synchronous/Asynchronous**: Synchronous

```python
"""
api/adapters/request_adapter.py

Maps external transport JSON payloads into internal domain Request entities.
"""
from typing import Dict, Any
from voxcore.contracts.runtime.models import Request

class RequestAdapter:
    """
    Adapter to convert DTOs into internal domain Request models.
    """
    
    def __init__(self) -> None:
        """
        Initializes the request adapter.
        """
        pass

    def to_domain(self, payload: Dict[str, Any]) -> Request:
        """
        Translates a validated JSON payload into a Request object.
        
        Args:
            payload: Validated JSON dictionary.
            
        Returns:
            Domain Request entity.
        """
        pass
```

---

### `api/adapters/response_adapter.py`

**Purpose**: Maps internal domain `Response` models into external DTOs.
**Public Class**: `ResponseAdapter`
**Abstract Interfaces**: None
**Constructor**: `__init__(self)`
**Public Methods**:
- `def to_dto(self, response: Response) -> dict` (Internal API)
**Return Types**: `dict`
**Expected Exceptions**: None
**Private Methods**: None
**Synchronous/Asynchronous**: Synchronous

```python
"""
api/adapters/response_adapter.py

Maps internal domain Response entities into JSON-serializable DTOs.
"""
from typing import Dict, Any
from voxcore.contracts.runtime.models import Response

class ResponseAdapter:
    """
    Adapter to convert internal domain Response models into DTOs.
    """
    
    def __init__(self) -> None:
        """
        Initializes the response adapter.
        """
        pass

    def to_dto(self, response: Response) -> Dict[str, Any]:
        """
        Translates a Response object into a JSON-serializable dictionary.
        
        Args:
            response: Domain Response entity.
            
        Returns:
            Formatted Response JSON dictionary.
        """
        pass
```

---

### `api/exception_translator.py`

**Purpose**: Translates internal domain exceptions into standardized transport error responses.
**Public Class**: `ExceptionTranslator`
**Abstract Interfaces**: None
**Constructor**: `__init__(self)`
**Public Methods**:
- `def translate(self, error: Exception) -> dict` (Internal API)
**Return Types**: `dict`
**Expected Exceptions**: None
**Private Methods**: `_map_status_code`
**Synchronous/Asynchronous**: Synchronous

```python
"""
api/exception_translator.py

Translates domain exceptions into standard transport errors.
"""
from typing import Dict, Any

class ExceptionTranslator:
    """
    Maps internal errors into standardized JSON error representations, ensuring internal state is obfuscated.
    """
    
    def __init__(self) -> None:
        """
        Initializes the exception translator.
        """
        pass

    def translate(self, error: Exception) -> Dict[str, Any]:
        """
        Translates a domain Exception into a standard Error JSON dictionary.
        
        Args:
            error: The caught exception.
            
        Returns:
            Standardized Error JSON dictionary.
        """
        pass

    def _map_status_code(self, error: Exception) -> int:
        """
        Determines the appropriate HTTP status code for a given exception type.
        """
        pass
```

---

### `api/runtime_gateway.py`

**Purpose**: Single entrypoint for the API package to invoke the internal VoxCore runtime execution pipeline.
**Public Class**: `RuntimeGateway`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, pipeline: RuntimeExecutionPipeline)`
**Public Methods**:
- `async submit_request(self, request: Request) -> Response` (Internal API)
**Return Types**: `Response`
**Expected Exceptions**: `Exception` (Domain errors)
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
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
        """
        pass

    async def submit_request(self, request: Request) -> Response:
        """
        Submits a mapped Request to the runtime pipeline for execution.
        
        Args:
            request: The domain Request entity.
            
        Returns:
            The resulting domain Response entity.
            
        Raises:
            Any domain exception thrown by the runtime.
        """
        pass
```
