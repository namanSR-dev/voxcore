"""
security/identity/identity_context.py

Standardized data model representing the authenticated caller.
"""
from typing import List

class IdentityContext:
    """
    Holds immutable claims and roles for the current execution scope.
    """
    def __init__(self, user_id: str, roles: List[str]) -> None:
        pass

    def has_role(self, role: str) -> bool:
        """
        Helper method to check if the identity holds a specific role.
        """
        pass
