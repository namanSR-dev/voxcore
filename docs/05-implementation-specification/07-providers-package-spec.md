# Providers Package Implementation Specification

## Package Path
`backend/voxcore/providers/`

## Folder Structure
```
providers/
├── __init__.py
├── adapters/
│   ├── __init__.py
│   └── provider_adapter_base.py
├── base/
│   ├── __init__.py
│   └── base_provider.py
├── capabilities/
│   ├── __init__.py
│   └── capability_manager.py
├── factories/
│   ├── __init__.py
│   └── provider_factory.py
├── lifecycle/
│   ├── __init__.py
│   └── provider_lifecycle.py
├── normalization/
│   ├── __init__.py
│   └── output_normalizer.py
├── registry/
│   ├── __init__.py
│   └── provider_registry.py
└── validation/
    ├── __init__.py
    └── schema_validator.py
```

---

## Files

### `providers/registry/provider_registry.py`

**Purpose**: Central ledger mapping provider names/IDs to their initialized instances.
**Public Class**: `ProviderRegistry`
**Abstract Interfaces**: None
**Constructor**: `__init__(self)`
**Public Methods**:
- `def register(self, name: str, provider: Any) -> None` (Internal API)
- `def get_provider(self, name: str) -> Any` (Internal API)
**Return Types**: `None`, `Any`
**Expected Exceptions**: `ProviderNotFoundError`
**Private Methods**: None
**Synchronous/Asynchronous**: Synchronous

```python
"""
providers/registry/provider_registry.py

Central ledger for tracking activated providers and their factory instances.
"""
from typing import Any, Dict

class ProviderRegistry:
    """
    Holds references to all registered providers available to the Runtime.
    """
    def __init__(self) -> None:
        pass

    def register(self, name: str, provider: Any) -> None:
        """
        Registers a new provider instance.
        """
        pass

    def get_provider(self, name: str) -> Any:
        """
        Retrieves an active provider by its unique identifier.
        """
        pass
```

---

### `providers/capabilities/capability_manager.py`

**Purpose**: Tracks which providers support which features (e.g., Vision, Function Calling).
**Public Class**: `CapabilityManager`
**Abstract Interfaces**: None
**Constructor**: `__init__(self)`
**Public Methods**:
- `def supports(self, provider: Any, capability: str) -> bool` (Internal API)
**Return Types**: `bool`
**Expected Exceptions**: None
**Private Methods**: None
**Synchronous/Asynchronous**: Synchronous

```python
"""
providers/capabilities/capability_manager.py

Tracks and queries the supported features (vision, tools, streaming) of active providers.
"""
from typing import Any

class CapabilityManager:
    """
    Manages capability bitmasks or registries for providers.
    """
    def __init__(self) -> None:
        pass

    def supports(self, provider: Any, capability: str) -> bool:
        """
        Returns true if the provider supports the requested capability.
        """
        pass
```

---

### `providers/normalization/output_normalizer.py`

**Purpose**: Standardizes the wildly different JSON responses from various LLM vendors into a unified VoxCore struct.
**Public Class**: `OutputNormalizer`
**Abstract Interfaces**: None
**Constructor**: `__init__(self)`
**Public Methods**:
- `def normalize(self, raw_response: dict, provider_type: str) -> Any` (Internal API)
**Return Types**: `Any` (Domain Response struct)
**Expected Exceptions**: `NormalizationError`
**Private Methods**: `_parse_openai`, `_parse_anthropic`
**Synchronous/Asynchronous**: Synchronous

```python
"""
providers/normalization/output_normalizer.py

Normalizes vendor-specific payload structures into universal domain models.
"""
from typing import Dict, Any

class OutputNormalizer:
    """
    Standardizes output payloads so the Runtime Package doesn't have to deal with vendor quirks.
    """
    def __init__(self) -> None:
        pass

    def normalize(self, raw_response: Dict[str, Any], provider_type: str) -> Any:
        """
        Converts a vendor response into a standard VoxCore Response struct.
        """
        pass

    def _parse_openai(self, raw: Dict[str, Any]) -> Any:
        pass

    def _parse_anthropic(self, raw: Dict[str, Any]) -> Any:
        pass
```

---

### `providers/adapters/provider_adapter_base.py`

**Purpose**: Provides common HTTP request and retry logic for concrete provider implementations.
**Public Class**: `ProviderAdapterBase`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, api_key: str, base_url: str)`
**Public Methods**:
- `async _execute_http(self, endpoint: str, payload: dict) -> dict` (Protected API)
**Return Types**: `dict`
**Expected Exceptions**: `HttpTransportError`
**Private Methods**: `_apply_retry_policy`
**Synchronous/Asynchronous**: Asynchronous

```python
"""
providers/adapters/provider_adapter_base.py

Provides common HTTP execution and resilience patterns for concrete providers.
"""
from typing import Dict, Any

class ProviderAdapterBase:
    """
    Base class providing resilient HTTP transport for AI vendor SDKs or REST endpoints.
    """
    def __init__(self, api_key: str, base_url: str) -> None:
        pass

    async def _execute_http(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes an HTTP request with built-in retries and circuit breakers.
        """
        pass

    def _apply_retry_policy(self) -> None:
        pass
```
