"""
api/adapters/request_adapter.py

Maps external transport JSON payloads into internal domain Request entities.
"""
from typing import Dict, Any
from voxcore.contracts.runtime.models import Request

class RequestAdapter:
    """
    Adapter to convert DTOs into internal domain Request models.
    """
    
    def __init__(self) -> None:
        """
        Initializes the request adapter.
        """
        pass

    def to_domain(self, payload: Dict[str, Any]) -> Request:
        """
        Translates a validated JSON payload into a Request object.
        
        Args:
            payload (Dict[str, Any]): Validated JSON dictionary.
            
        Returns:
            Request: Domain Request entity.
        """
        pass
