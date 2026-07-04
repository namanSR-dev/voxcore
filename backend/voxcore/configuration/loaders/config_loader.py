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
        """
        Initializes the config loader.
        
        Args:
            providers (List[Any]): A list of configuration providers (e.g., EnvProvider, YamlProvider).
        """
        pass

    def load_all(self) -> Dict[str, Any]:
        """
        Loads raw configurations from all providers.
        
        Returns:
            Dict[str, Any]: Dict containing raw configuration values.
        """
        pass

    def _fetch_from_provider(self, provider: Any) -> Dict[str, Any]:
        """
        Internal helper to fetch data from a single provider safely.
        
        Args:
            provider (Any): The provider instance to fetch from.
            
        Returns:
            Dict[str, Any]: The loaded configuration subset.
        """
        pass
