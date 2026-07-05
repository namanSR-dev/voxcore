"""
api/exception_translator.py

Translates domain exceptions into standard transport errors.
"""
from typing import Dict, Any

class ExceptionTranslator:
    """
    Maps internal errors into standardized JSON error representations, ensuring internal state is obfuscated.
    """
    def __init__(self) -> None:
        pass

    def translate(self, error: Exception) -> Dict[str, Any]:
        status_code = self._map_status_code(error)
        return {
            "error": type(error).__name__,
            "message": str(error),
            "status_code": status_code
        }

    def _map_status_code(self, error: Exception) -> int:
        if isinstance(error, ValueError):
            return 400
        return 500
