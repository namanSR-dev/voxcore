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
    """
    id: str
    session_id: str
    payload: Dict[str, Any]

@dataclass(frozen=True)
class Response:
    """
    Immutable representation of the system's generated output.
    """
    id: str
    request_id: str
    output: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
