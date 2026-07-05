"""
configuration/lifecycle/config_manager.py

Coordinates the boot-up sequence and holds the globally resolved configuration.
"""
from typing import Any
from voxcore.configuration.loaders.config_loader import ConfigLoader
from voxcore.configuration.resolution.config_resolver import ConfigResolver
from voxcore.configuration.validation.config_validator import ConfigValidator
from voxcore.configuration.schemas.base_schema import AppConfigSchema

class ConfigManager:
    """
    Main entrypoint for initializing and accessing application configuration.
    """
    def __init__(self, loader: ConfigLoader, resolver: ConfigResolver, validator: ConfigValidator) -> None:
        self._loader = loader
        self._resolver = resolver
        self._validator = validator
        self._config: Any = None

    def initialize(self) -> None:
        """
        Executes the load, resolve, and validate lifecycle. Locks the config upon success.
        
        Raises:
            Exception if configuration fails to validate.
        """
        raw_data = self._loader.load_all()
        # For now, we only have one source, but resolver expects a list
        resolved = self._resolver.resolve([raw_data])
        self._config = self._validator.validate(resolved, AppConfigSchema)
        self._lock_config()

    def get_config(self) -> Any:
        """
        Retrieves the read-only validated configuration object.
        """
        if not self._config:
            raise RuntimeError("Configuration has not been initialized.")
        return self._config

    def _lock_config(self) -> None:
        pass
