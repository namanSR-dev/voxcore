"""
plugins/lifecycle/plugin_manager.py
Coordinates the complete lifecycle of third-party platform extensions.
"""
from voxcore.plugins.discovery.plugin_scanner import PluginScanner
from voxcore.plugins.validation.manifest_validator import ManifestValidator
from voxcore.plugins.dependencies.dependency_resolver import DependencyResolver
from voxcore.plugins.extension_points.extension_registry import ExtensionRegistry
from typing import Any

class PluginManager:
    """
    Main entrypoint for managing the plugin subsystem.
    """
    def __init__(self, scanner: PluginScanner, validator: ManifestValidator, resolver: DependencyResolver, registry: ExtensionRegistry) -> None:
        self.scanner = scanner
        self.validator = validator
        self.resolver = resolver
        self.registry = registry

    def initialize_plugins(self) -> None:
        """
        Discovers, validates, resolves, and activates all available plugins.
        """
        plugins = self.scanner.discover()
        valid = [p for p in plugins if self.validator.validate(p)]
        ordered = self.resolver.resolve_order(valid)
        for p in ordered:
            self._activate_plugin(p)

    def shutdown_plugins(self) -> None:
        """
        Deactivates all plugins gracefully during system shutdown.
        """
        pass

    def _activate_plugin(self, plugin: Any) -> None:
        pass
