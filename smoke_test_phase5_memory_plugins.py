import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from voxcore.memory.retrieval.memory_retriever import MemoryRetriever
from voxcore.memory.ranking.relevance_scorer import RelevanceScorer
from voxcore.memory.composition.context_assembler import ContextAssembler
from voxcore.memory.lifecycle.memory_manager import MemoryManager

from voxcore.plugins.discovery.plugin_scanner import PluginScanner
from voxcore.plugins.validation.manifest_validator import ManifestValidator
from voxcore.plugins.dependencies.dependency_resolver import DependencyResolver
from voxcore.plugins.extension_points.extension_registry import ExtensionRegistry
from voxcore.plugins.lifecycle.plugin_manager import PluginManager

async def main():
    print("=== Testing Memory Subsystem ===")
    retriever = MemoryRetriever(store=None)
    scorer = RelevanceScorer()
    assembler = ContextAssembler(max_tokens=4000)
    
    memory_manager = MemoryManager(retriever, scorer, assembler)
    context = await memory_manager.get_context("Hello AI")
    print(f"✅ Context assembled successfully: '{context}'")
    
    print("\n=== Testing Plugin Subsystem ===")
    scanner = PluginScanner(["./plugins"])
    validator = ManifestValidator(core_version="1.0.0")
    resolver = DependencyResolver()
    registry = ExtensionRegistry()
    
    plugin_manager = PluginManager(scanner, validator, resolver, registry)
    plugin_manager.initialize_plugins()
    plugin_manager.shutdown_plugins()
    print("✅ Plugin Manager booted and shutdown successfully (0 plugins found)!")

if __name__ == "__main__":
    asyncio.run(main())
