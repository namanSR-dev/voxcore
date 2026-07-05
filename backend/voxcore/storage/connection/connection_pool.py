"""
storage/connection/connection_pool.py

Manages reusable connections to relational databases using SQLAlchemy.
"""
from typing import Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

class ConnectionPool:
    """
    Maintains a pool of active database connections to reduce latency.
    """
    def __init__(self, dsn: str, pool_size: int = 5) -> None:
        # SQLite doesn't support standard connection pooling arguments
        kwargs = {}
        if not dsn.startswith("sqlite"):
            kwargs["pool_size"] = pool_size
            kwargs["max_overflow"] = 10
            
        self.engine = create_async_engine(dsn, **kwargs)
        self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)

    async def acquire(self) -> AsyncSession:
        """
        Leases a connection from the pool.
        """
        return self.session_maker()

    async def release(self, connection: AsyncSession) -> None:
        """
        Returns a connection to the pool.
        """
        await connection.close()

    async def _ping(self, connection: Any) -> bool:
        return True
