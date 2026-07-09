import asyncio
import os
import hashlib
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

# Import the base and models
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from voxcore.storage.database.core import Base, DATABASE_URL
from voxcore.storage.database.orm_models import User, Project, ApiKey

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def seed():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        # Create a Demo User
        user = User(email="demo@voxcore.ai", hashed_password="fake_hash")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        # Create a Demo Project
        persona = "You are VoxCore Demo, a highly energetic and helpful AI. Keep your answers extremely short and punchy."
        project = Project(user_id=user.id, name="Demo Health Assistant", domain_persona=persona)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        # Create a Demo API Key
        raw_key = "vox_test_12345"
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        
        api_key = ApiKey(
            project_id=project.id,
            key_hash=key_hash,
            prefix="vox_test_",
            is_active=True
        )
        session.add(api_key)
        await session.commit()
        
        print("\n\n" + "="*50)
        print("DATABASE SUCCESSFULLY SEEDED!")
        print("="*50)
        print(f"User: {user.email}")
        print(f"Project: {project.name}")
        print(f"API Key to use in frontend: {raw_key}")
        print("="*50 + "\n\n")

if __name__ == "__main__":
    asyncio.run(seed())
