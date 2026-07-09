import hashlib
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from voxcore.contracts.storage.i_project_repository import IProjectRepository
from voxcore.contracts.domain.models import ProjectDomain
from voxcore.storage.database.orm_models import ApiKey, Project

class SqlProjectRepository(IProjectRepository):
    """
    SQLAlchemy implementation of the IProjectRepository.
    Maps ORM objects into pure Pydantic Domain models.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    def _hash_api_key(self, api_key: str) -> str:
        """API Keys are high-entropy, so a fast SHA-256 hash is appropriate and allows direct equality queries."""
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    async def get_project_by_api_key(self, api_key: str) -> Optional[ProjectDomain]:
        hashed_key = self._hash_api_key(api_key)
        
        # We need the ApiKey and its associated Project
        stmt = (
            select(ApiKey)
            .options(selectinload(ApiKey.project))
            .where(ApiKey.key_hash == hashed_key)
            .where(ApiKey.is_active == True)
        )
        
        result = await self.session.execute(stmt)
        api_key_record = result.scalar_one_or_none()
        
        if not api_key_record or not api_key_record.project:
            return None
            
        return ProjectDomain.model_validate(api_key_record.project)

    async def get_project_by_id(self, project_id: int) -> Optional[ProjectDomain]:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        project_record = result.scalar_one_or_none()
        
        if not project_record:
            return None
            
        return ProjectDomain.model_validate(project_record)

    async def get_project_persona(self, project_id: int) -> Optional[str]:
        stmt = select(Project.domain_persona).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_project_persona(self, project_id: int, persona: str) -> bool:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        project = result.scalar_one_or_none()
        
        if not project:
            return False
            
        project.domain_persona = persona
        await self.session.commit()
        return True
