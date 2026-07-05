"""
runtime/context/runtime_context.py

Holds execution-scoped variables, tracking state throughout the pipeline.
"""
from typing import Any, Dict

class RuntimeContext:
    """
    State container passed through the execution pipeline.
    """
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """
        Stores a value in the context.
        """
        self._store[key] = value

    def get(self, key: str) -> Any:
        """
        Retrieves a value from the context.
        """
        if key not in self._store:
            raise KeyError(f"Key '{key}' not found in RuntimeContext")
        return self._store[key]
