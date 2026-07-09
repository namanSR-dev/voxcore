from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserDomain(BaseModel):
    """Domain model representing a system User/Tenant."""
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)

class ProjectDomain(BaseModel):
    """Domain model representing a specific AI Agent Project configuration."""
    id: int
    user_id: int
    name: str
    domain_persona: str

    model_config = ConfigDict(from_attributes=True)

class ApiKeyDomain(BaseModel):
    """Domain model representing an API Key mapped to a project."""
    id: int
    project_id: int
    prefix: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
