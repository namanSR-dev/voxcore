# Storage Package Implementation Specification

## Package Path
`backend/voxcore/storage/`

## Folder Structure
```
storage/
├── __init__.py
├── adapters/
│   ├── __init__.py
│   ├── postgres_adapter.py
│   └── chroma_adapter.py
├── caching/
│   ├── __init__.py
│   └── query_cache.py
├── connection/
│   ├── __init__.py
│   └── connection_pool.py
├── migrations/
│   ├── __init__.py
│   └── schema_migrator.py
├── repositories/
│   ├── __init__.py
│   ├── memory_repository.py
│   └── session_repository.py
└── unit_of_work/
    ├── __init__.py
    └── transaction_manager.py
```

---

## Files

### `storage/connection/connection_pool.py`

**Purpose**: Manages reusable database connections to prevent exhausting external database resources.
**Public Class**: `ConnectionPool`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, dsn: str, pool_size: int)`
**Public Methods**:
- `async acquire(self) -> Any` (Internal API)
- `async release(self, connection: Any) -> None` (Internal API)
**Return Types**: Database connection object
**Expected Exceptions**: `PoolExhaustedError`, `ConnectionError`
**Private Methods**: `_ping`
**Synchronous/Asynchronous**: Asynchronous

```python
"""
storage/connection/connection_pool.py

Manages reusable connections to relational or vector databases.
"""
from typing import Any

class ConnectionPool:
    """
    Maintains a pool of active database connections to reduce latency.
    """
    def __init__(self, dsn: str, pool_size: int) -> None:
        pass

    async def acquire(self) -> Any:
        """
        Leases a connection from the pool.
        """
        pass

    async def release(self, connection: Any) -> None:
        """
        Returns a connection to the pool.
        """
        pass

    async def _ping(self, connection: Any) -> bool:
        pass
```

---

### `storage/repositories/memory_repository.py`

**Purpose**: Concrete implementation of the memory storage contract, bridging domain entities to SQL/Vector commands.
**Public Class**: `MemoryRepository`
**Abstract Interfaces**: Implements `IMemoryStore`
**Constructor**: `__init__(self, connection_pool: ConnectionPool)`
**Public Methods**:
- `async save(self, memory_node: Any) -> None` (Public API)
- `async query_by_vector(self, vector: list[float], limit: int) -> list[Any]` (Public API)
**Return Types**: `None`, `list`
**Expected Exceptions**: `DatabaseError`
**Private Methods**: `_map_to_domain`, `_map_to_record`
**Synchronous/Asynchronous**: Asynchronous

```python
"""
storage/repositories/memory_repository.py

Implements data access for conversational and semantic memory.
"""
from typing import List, Any
from voxcore.storage.connection.connection_pool import ConnectionPool
from voxcore.contracts.memory.i_memory_store import IMemoryStore

class MemoryRepository(IMemoryStore):
    """
    Translates domain memory operations into raw database queries.
    """
    def __init__(self, connection_pool: ConnectionPool) -> None:
        pass

    async def save(self, memory_node: Any) -> None:
        """
        Persists a memory node to the database.
        """
        pass

    async def query_by_vector(self, vector: List[float], limit: int) -> List[Any]:
        """
        Executes a similarity search against the underlying vector store.
        """
        pass

    def _map_to_domain(self, record: Any) -> Any:
        pass

    def _map_to_record(self, entity: Any) -> Any:
        pass
```

---

### `storage/unit_of_work/transaction_manager.py`

**Purpose**: Guarantees atomic operations when persisting across multiple repositories.
**Public Class**: `TransactionManager`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, connection_pool: ConnectionPool)`
**Public Methods**:
- `async begin(self) -> Any` (Internal API)
- `async commit(self, tx: Any) -> None` (Internal API)
- `async rollback(self, tx: Any) -> None` (Internal API)
**Return Types**: Transaction reference
**Expected Exceptions**: `TransactionError`
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
"""
storage/unit_of_work/transaction_manager.py

Provides transactional boundaries for complex state changes.
"""
from typing import Any
from voxcore.storage.connection.connection_pool import ConnectionPool

class TransactionManager:
    """
    Ensures ACID properties when persisting multiple entities simultaneously.
    """
    def __init__(self, connection_pool: ConnectionPool) -> None:
        pass

    async def begin(self) -> Any:
        """
        Starts a database transaction.
        """
        pass

    async def commit(self, tx: Any) -> None:
        """
        Commits a successful transaction.
        """
        pass

    async def rollback(self, tx: Any) -> None:
        """
        Rolls back a failed transaction.
        """
        pass
```

---

### `storage/caching/query_cache.py`

**Purpose**: Provides ephemeral, fast-access memory (e.g., Redis) for frequently accessed, unchanging records.
**Public Class**: `QueryCache`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, ttl_seconds: int)`
**Public Methods**:
- `async get(self, key: str) -> Any` (Internal API)
- `async set(self, key: str, value: Any) -> None` (Internal API)
**Return Types**: `Any`, `None`
**Expected Exceptions**: `CacheUnavailableError`
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
"""
storage/caching/query_cache.py

Reduces database load by caching common query results.
"""
from typing import Any

class QueryCache:
    """
    In-memory or distributed cache wrapper.
    """
    def __init__(self, ttl_seconds: int) -> None:
        pass

    async def get(self, key: str) -> Any:
        """
        Retrieves a cached value, or None if expired/missing.
        """
        pass

    async def set(self, key: str, value: Any) -> None:
        """
        Stores a value in the cache with the configured TTL.
        """
        pass
```
