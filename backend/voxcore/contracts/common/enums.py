"""
contracts/common/enums.py

Shared enumerations used across multiple packages.
"""
from enum import Enum

class Role(str, Enum):
    """
    Standard user roles for authorization.
    """
    ADMIN = "admin"
    USER = "user"
    SYSTEM = "system"

class ProviderType(str, Enum):
    """
    Types of AI providers supported by the system.
    """
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
