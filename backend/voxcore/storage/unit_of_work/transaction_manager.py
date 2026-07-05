"""
storage/unit_of_work/transaction_manager.py

Provides transactional boundaries for complex state changes.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from voxcore.storage.connection.connection_pool import ConnectionPool

class TransactionManager:
    """
    Ensures ACID properties when persisting multiple entities simultaneously.
    """
    def __init__(self, connection_pool: ConnectionPool) -> None:
        self.pool = connection_pool

    async def begin(self) -> AsyncSession:
        """
        Starts a database transaction.
        """
        session = await self.pool.acquire()
        return session

    async def commit(self, tx: AsyncSession) -> None:
        """
        Commits a successful transaction.
        """
        try:
            await tx.commit()
        finally:
            await self.pool.release(tx)

    async def rollback(self, tx: AsyncSession) -> None:
        """
        Rolls back a failed transaction.
        """
        try:
            await tx.rollback()
        finally:
            await self.pool.release(tx)
