# Memory Package Implementation Specification

## Package Path
`backend/voxcore/memory/`

## Folder Structure
```
memory/
├── __init__.py
├── composition/
│   ├── __init__.py
│   └── context_assembler.py
├── diagnostics/
│   ├── __init__.py
│   └── memory_auditor.py
├── indexing/
│   ├── __init__.py
│   └── memory_indexer.py
├── lifecycle/
│   ├── __init__.py
│   └── memory_manager.py
├── policies/
│   ├── __init__.py
│   └── eviction_policy.py
├── ranking/
│   ├── __init__.py
│   └── relevance_scorer.py
├── retrieval/
│   ├── __init__.py
│   └── memory_retriever.py
├── summarization/
│   ├── __init__.py
│   └── memory_summarizer.py
└── validation/
    ├── __init__.py
    └── memory_validator.py
```

---

## Files

### `memory/retrieval/memory_retriever.py`

**Purpose**: Fetches raw candidate memories from the storage layer via Contracts.
**Public Class**: `MemoryRetriever`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, store: IMemoryStore)`
**Public Methods**:
- `async retrieve(self, query_vector: list[float], limit: int) -> list[Any]` (Internal API)
**Return Types**: `list`
**Expected Exceptions**: `StorageTimeoutError`
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
"""
memory/retrieval/memory_retriever.py

Fetches candidate memories from the persistence layer without executing business logic.
"""
from typing import List, Any
from voxcore.contracts.memory.i_memory_store import IMemoryStore

class MemoryRetriever:
    """
    Coordinates the fetching of candidate memories from storage.
    """
    def __init__(self, store: IMemoryStore) -> None:
        pass

    async def retrieve(self, query_vector: List[float], limit: int) -> List[Any]:
        """
        Retrieves top N candidate memories based on vector similarity.
        """
        pass
```

---

### `memory/ranking/relevance_scorer.py`

**Purpose**: Scores and sorts candidate memories based on semantic similarity and recency decay.
**Public Class**: `RelevanceScorer`
**Abstract Interfaces**: None
**Constructor**: `__init__(self)`
**Public Methods**:
- `def rank(self, candidates: list[Any]) -> list[Any]` (Internal API)
**Return Types**: `list`
**Expected Exceptions**: None
**Private Methods**: `_apply_recency_decay`
**Synchronous/Asynchronous**: Synchronous

```python
"""
memory/ranking/relevance_scorer.py

Scores and sorts retrieved memories based on relevance heuristics.
"""
from typing import List, Any

class RelevanceScorer:
    """
    Applies mathematical ranking to memory candidates.
    """
    def __init__(self) -> None:
        pass

    def rank(self, candidates: List[Any]) -> List[Any]:
        """
        Sorts candidates descending by their calculated relevance score.
        """
        pass

    def _apply_recency_decay(self, candidate: Any) -> float:
        pass
```

---

### `memory/composition/context_assembler.py`

**Purpose**: Assembles ranked memories into the final token-budgeted prompt payload.
**Public Class**: `ContextAssembler`
**Abstract Interfaces**: None
**Constructor**: `__init__(self, max_tokens: int)`
**Public Methods**:
- `def assemble(self, ranked_memories: list[Any], current_prompt: str) -> str` (Internal API)
**Return Types**: `str`
**Expected Exceptions**: `ContextBudgetExceededError`
**Private Methods**: `_truncate`, `_deduplicate`
**Synchronous/Asynchronous**: Synchronous

```python
"""
memory/composition/context_assembler.py

Assembles the final context string, enforcing token limits and priority ordering.
"""
from typing import List, Any

class ContextAssembler:
    """
    Constructs the prompt payload that will be sent to the LLM.
    """
    def __init__(self, max_tokens: int) -> None:
        pass

    def assemble(self, ranked_memories: List[Any], current_prompt: str) -> str:
        """
        Builds the context string, ensuring it fits within the token budget.
        """
        pass

    def _truncate(self, text: str) -> str:
        pass
        
    def _deduplicate(self, memories: List[Any]) -> List[Any]:
        pass
```

---

### `memory/lifecycle/memory_manager.py`

**Purpose**: Orchestrates the transitions of memory from creation to retrieval and eviction.
**Public Class**: `MemoryManager`
**Abstract Interfaces**: Implements `IMemoryService`
**Constructor**: `__init__(self, retriever: MemoryRetriever, scorer: RelevanceScorer, assembler: ContextAssembler)`
**Public Methods**:
- `async get_context(self, prompt: str) -> str` (Public API)
- `async add_memory(self, text: str) -> None` (Public API)
**Return Types**: `str` / `None`
**Expected Exceptions**: `Exception`
**Private Methods**: None
**Synchronous/Asynchronous**: Asynchronous

```python
"""
memory/lifecycle/memory_manager.py

Orchestrates the entire memory lifecycle, providing the public API for the Memory package.
"""
from voxcore.memory.retrieval.memory_retriever import MemoryRetriever
from voxcore.memory.ranking.relevance_scorer import RelevanceScorer
from voxcore.memory.composition.context_assembler import ContextAssembler

class MemoryManager:
    """
    The primary service facade for interacting with the Memory package.
    """
    def __init__(self, retriever: MemoryRetriever, scorer: RelevanceScorer, assembler: ContextAssembler) -> None:
        pass

    async def get_context(self, prompt: str) -> str:
        """
        Retrieves, ranks, and assembles memory context for a given prompt.
        """
        pass

    async def add_memory(self, text: str) -> None:
        """
        Validates, indexes, and persists a new memory node.
        """
        pass
```
