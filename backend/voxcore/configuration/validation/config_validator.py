"""
configuration/validation/config_validator.py

Enforces schema correctness and type casting on resolved configurations.
"""
from typing import Dict, Any

class ConfigValidator:
    """
    Validates that a resolved configuration dictionary matches the target schema.
    """
    def __init__(self) -> None:
        pass

    def validate(self, resolved_config: Dict[str, Any], schema: Any) -> Any:
        """
        Validates and instantiates the schema with the resolved values.
        
        Raises:
            ValidationError if required fields are missing or types are mismatched.
        """
        self._enforce_required()
        self._check_types()
        # Pydantic handles the actual validation upon instantiation
        return schema(**resolved_config)

    def _check_types(self) -> None:
        pass

    def _enforce_required(self) -> None:
        pass
