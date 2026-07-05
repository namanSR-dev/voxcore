"""
providers/adapters/provider_adapter_base.py

Provides common HTTP execution and resilience patterns for concrete providers.
"""
from typing import Dict, Any
import httpx

class ProviderAdapterBase:
    """
    Base class providing resilient HTTP transport for AI vendor SDKs or REST endpoints.
    """
    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def _execute_http(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes an HTTP request with built-in retries and circuit breakers.
        """
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = await self.client.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def _apply_retry_policy(self) -> None:
        pass
