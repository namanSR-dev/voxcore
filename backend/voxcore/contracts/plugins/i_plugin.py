"""
contracts/plugins/i_plugin.py

Defines the lifecycle interface for external platform extensions.
"""
from typing import Any
from abc import ABC, abstractmethod

class IPlugin(ABC):
    """
    Abstract interface for VoxCore plugins to contribute capabilities.
    """
    
    @abstractmethod
    def activate(self, registry: Any) -> None:
        """
        Invoked when the plugin is booted. The plugin should register its tools or providers here.
        """
        pass

    @abstractmethod
    def deactivate(self) -> None:
        """
        Invoked during shutdown to allow the plugin to clean up resources.
        """
        pass
