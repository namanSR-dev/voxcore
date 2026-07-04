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
