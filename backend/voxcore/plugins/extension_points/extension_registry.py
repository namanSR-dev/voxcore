"""
plugins/extension_points/extension_registry.py
The safe sandbox object passed to plugins to allow them to contribute capabilities.
"""
from typing import Any

class ExtensionRegistry:
    """
    Provides the hooks that plugins use to inject capabilities into VoxCore.
    """
    def __init__(self) -> None:
        pass

    def register_provider(self, provider: Any) -> None:
        """
        Allows a plugin to contribute an LLM or AI provider implementation.
        """
        pass

    def register_tool(self, tool: Any) -> None:
        """
        Allows a plugin to contribute an executable Tool.
        """
        pass
