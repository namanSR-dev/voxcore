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
        """
        Initializes the response adapter.
        """
        pass

    def to_dto(self, response: Response) -> Dict[str, Any]:
        """
        Translates a Response object into a JSON-serializable dictionary.
        
        Args:
            response (Response): Domain Response entity.
            
        Returns:
            Dict[str, Any]: Formatted Response JSON dictionary.
        """
        pass
