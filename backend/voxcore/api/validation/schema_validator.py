"""
api/validation/schema_validator.py

Validates incoming JSON payloads to ensure they match expected constraints.
"""
from typing import Dict, Any
from pydantic import BaseModel, ValidationError

class InferenceRequestSchema(BaseModel):
    prompt: str
    session_id: str | None = None
    stream: bool = False

class SchemaValidator:
    """
    Enforces structural limits on inbound requests before they touch the runtime.
    """
    def __init__(self) -> None:
        pass

    def validate_request(self, payload: Dict[str, Any]) -> bool:
        try:
            InferenceRequestSchema(**payload)
            return True
        except ValidationError as e:
            raise ValueError(f"Schema violation: {e}")
