"""
security/authorization/policy_enforcer.py

Evaluates role-based or attribute-based access control policies.
"""
from typing import Any, Dict
from voxcore.contracts.security.i_authorizer import IAuthorizer
from voxcore.contracts.common.errors import AuthorizationError

class PolicyEnforcer(IAuthorizer):
    """
    Determines whether a known identity is allowed to perform a requested action.
    """
    def __init__(self, roles_mapping: Dict[str, Any]) -> None:
        self.roles_mapping = roles_mapping

    def authorize(self, identity: Any, action: str, resource: str) -> bool:
        """
        Checks if the identity has permission for the action on the resource.
        """
        # A simple RBAC (Role-Based Access Control) implementation
        for role in getattr(identity, "roles", []):
            if self._evaluate_policy(role, action):
                return True
                
        raise AuthorizationError(f"Identity lacks permission for {action} on {resource}")

    def _evaluate_policy(self, role: str, action: str) -> bool:
        allowed_actions = self.roles_mapping.get(role, [])
        return action in allowed_actions or "*" in allowed_actions
