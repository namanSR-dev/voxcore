"""
contracts/security/i_authorizer.py

Defines the contract for role-based and attribute-based access control.
"""
from typing import Any
from abc import ABC, abstractmethod

class IAuthorizer(ABC):
    """
    Abstract interface for evaluating security policies against caller identities.
    """
    
    @abstractmethod
    def authorize(self, identity: Any, action: str, resource: str) -> bool:
        """
        Evaluates whether the given identity is allowed to perform the action on the resource.
        """
        pass
