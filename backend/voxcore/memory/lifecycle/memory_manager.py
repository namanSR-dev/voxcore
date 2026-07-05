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
        self.retriever = retriever
        self.scorer = scorer
        self.assembler = assembler

    async def get_context(self, prompt: str) -> str:
        """
        Retrieves, ranks, and assembles memory context for a given prompt.
        """
        candidates = await self.retriever.retrieve([], 10)
        ranked = self.scorer.rank(candidates)
        return self.assembler.assemble(ranked, prompt)

    async def add_memory(self, text: str) -> None:
        """
        Validates, indexes, and persists a new memory node.
        """
        pass
