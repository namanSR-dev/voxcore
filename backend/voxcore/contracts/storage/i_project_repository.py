from abc import ABC, abstractmethod
from typing import Optional
from voxcore.contracts.domain.models import ProjectDomain

class IProjectRepository(ABC):
    """
    Abstract interface for retrieving Project data.
    Shields the core application from database specifics (SQLAlchemy, ORM state).
    """
    
    @abstractmethod
    async def get_project_by_api_key(self, api_key: str) -> Optional[ProjectDomain]:
        """
        Retrieves a project using its associated hashed API key.
        Returns a pure Pydantic ProjectDomain object.
        """
        pass
    
    @abstractmethod
    async def get_project_by_id(self, project_id: int) -> Optional[ProjectDomain]:
        """
        Retrieves a project by its internal ID.
        """
        pass
