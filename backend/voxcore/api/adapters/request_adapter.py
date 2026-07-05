"""
api/adapters/request_adapter.py

Maps external transport JSON payloads into internal domain Request entities.
"""
from typing import Dict, Any
import uuid
from voxcore.contracts.runtime.models import Request

class RequestAdapter:
    """
    Adapter to convert DTOs into internal domain Request models.
    """
    def __init__(self) -> None:
        pass

    def to_domain(self, payload: Dict[str, Any]) -> Request:
        prompt = payload.get("prompt", "")
        session_id = payload.get("session_id") or str(uuid.uuid4())
        return Request(
            id=str(uuid.uuid4()),
            session_id=session_id,
            payload={"text": prompt}
        )
