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
