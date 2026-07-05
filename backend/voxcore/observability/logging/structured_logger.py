"""
observability/logging/structured_logger.py

Provides structured JSON logging for the VoxCore platform.
"""
from typing import Any
import structlog
import logging
import sys

class StructuredLogger:
    """
    Standard logger that ensures all platform logs conform to a parsable JSON schema.
    """
    def __init__(self, service_name: str) -> None:
        # Basic configuration to output JSON to stdout
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )
        self._logger = structlog.get_logger(service_name)

    def info(self, message: str, **kwargs: Any) -> None:
        """
        Records an informational log event.
        """
        self._logger.info(message, **kwargs)

    def error(self, message: str, error: Exception, **kwargs: Any) -> None:
        """
        Records an error log event, attaching stack traces.
        """
        self._logger.error(message, error=str(error), **kwargs)

    def _format_log(self, level: str, message: str, **kwargs: Any) -> str:
        # Used internally if we ever need to bypass structlog
        return f"[{level}] {message} {kwargs}"
