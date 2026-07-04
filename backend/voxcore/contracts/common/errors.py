"""
contracts/common/errors.py

Shared exceptions used across multiple packages.
"""

class VoxCoreError(Exception):
    """
    Base exception for all custom VoxCore errors.
    """
    pass

class ConfigurationError(VoxCoreError):
    """
    Raised when required configuration is missing or invalid.
    """
    pass

class ProviderError(VoxCoreError):
    """
    Raised when an AI provider fails to execute.
    """
    pass

class AuthenticationError(VoxCoreError):
    """
    Raised when identity verification fails.
    """
    pass

class AuthorizationError(VoxCoreError):
    """
    Raised when an authenticated identity lacks required permissions.
    """
    pass
