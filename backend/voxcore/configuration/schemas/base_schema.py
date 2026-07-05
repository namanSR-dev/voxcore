"""
configuration/schemas/base_schema.py

Defines the strongly typed configuration schema using Pydantic.
"""
from pydantic import BaseModel, Field
from typing import Optional

class AppConfigSchema(BaseModel):
    """
    The master schema for application configuration.
    """
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = Field(default="HS256")
    ollama_base_url: Optional[str] = None
    openai_api_key: Optional[str] = None
