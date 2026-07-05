"""
configuration/loaders/config_loader.py

Orchestrates retrieving raw data from external configuration sources via providers.
"""
from typing import Dict, Any, List

class ConfigLoader:
    """
    Retrieves raw configuration data from multiple registered providers.
    """
    def __init__(self, providers: List[Any]) -> None:
        self._providers = providers

    def load_all(self) -> Dict[str, Any]:
        """
        Loads raw configurations from all providers.
        
        Returns:
            Dict containing raw configuration values.
        """
        combined = {}
        for provider in self._providers:
            data = self._fetch_from_provider(provider)
            combined.update(data)
        return combined

    def _fetch_from_provider(self, provider: Any) -> Dict[str, Any]:
        return provider.fetch()
