"""
api/adapters/response_adapter.py

Maps internal domain Response entities into JSON-serializable DTOs.
"""
from typing import Dict, Any
from voxcore.contracts.runtime.models import Response

class ResponseAdapter:
    """
    Adapter to convert internal domain Response models into DTOs.
    """
    def __init__(self) -> None:
        pass

    def to_dto(self, response: Response) -> Dict[str, Any]:
        return {
            "id": response.id,
            "request_id": response.request_id,
            "output": response.output
        }
