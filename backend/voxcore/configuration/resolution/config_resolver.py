"""
configuration/resolution/config_resolver.py

Merges multiple configuration sources deterministically based on precedence.
"""
from typing import Dict, Any, List

class ConfigResolver:
    """
    Resolves conflicting configuration keys using strict priority rules.
    """
    def __init__(self) -> None:
        pass

    def resolve(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merges a list of configurations, applying later dicts as overrides.
        """
        merged: Dict[str, Any] = {}
        for config in configs:
            merged = self._deep_merge(merged, config)
        return merged

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result = base.copy()
        result.update(override)
        return result
