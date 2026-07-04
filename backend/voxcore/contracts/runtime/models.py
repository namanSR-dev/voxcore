"""
contracts/runtime/models.py

Pure data structures representing the core domain entities exchanged between packages.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class Request:
    """
    Immutable representation of an inbound user prompt or action request.
    
    Attributes:
        id (str): A unique identifier for this specific request.
        session_id (str): The identifier of the conversational session.
        payload (Dict[str, Any]): The actual data or text input of the request.
    """
    id: str
    session_id: str
    payload: Dict[str, Any]

@dataclass(frozen=True)
class Response:
    """
    Immutable representation of the system's generated output.
    
    Attributes:
        id (str): A unique identifier for this specific response.
        request_id (str): The ID of the Request that triggered this Response.
        output (Dict[str, Any]): The generated output payload.
        metadata (Optional[Dict[str, Any]]): Optional diagnostic or routing metadata.
    """
    id: str
    request_id: str
    output: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
