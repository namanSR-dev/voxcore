import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///voxcore.db")

# connect_args={"timeout": 30} ensures secondary queries queue up gracefully 
# during heavy Voice AI micro-writes instead of throwing immediate "database is locked" errors.
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={"timeout": 30} if "sqlite" in DATABASE_URL else {}
)

# Explicitly configure SQLite PRAGMAs for high-concurrency (WAL mode)
# Using the sync engine API for event hooks is required for SQLite PRAGMAs in SQLAlchemy
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency injection generator for FastAPI routes if needed."""
    async with AsyncSessionLocal() as session:
        yield session
