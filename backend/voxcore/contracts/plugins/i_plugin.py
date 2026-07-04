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
        
        Args:
            registry (Any): The system registry where the plugin can inject its capabilities.
        """
        pass

    @abstractmethod
    def deactivate(self) -> None:
        """
        Invoked during system shutdown to allow the plugin to safely clean up resources.
        """
        pass
