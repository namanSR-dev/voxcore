"""
configuration/providers/env_provider.py

Loads configuration values from environment variables.
"""
from typing import Dict, Any
import os
from dotenv import load_dotenv

class EnvProvider:
    """
    Concrete implementation of a configuration provider that reads from os.environ.
    """
    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix
        # Ensure .env is loaded into os.environ
        load_dotenv()

    def fetch(self) -> Dict[str, Any]:
        """
        Fetches relevant environment variables.
        """
        return self._filter_keys()

    def _filter_keys(self) -> Dict[str, str]:
        result = {}
        for k, v in os.environ.items():
            if k.startswith(self.prefix):
                result[k.lower()] = v
        return result
