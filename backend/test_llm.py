import asyncio
import uuid
import os
from voxcore.storage.adapters.in_memory_store import InMemoryStore
from voxcore.memory.composition.context_builder import ContextBuilder
from voxcore.memory.lifecycle.session_manager import SessionMemoryManager
from voxcore.providers.adapters.groq_adapter import GroqAdapter
from voxcore.api.runtime_gateway import RuntimeGateway
from voxcore.runtime.pipeline.execution_pipeline import RuntimeExecutionPipeline
from voxcore.contracts.runtime.models import Request
from dotenv import load_dotenv

# Minimal provider registry
class DummyRegistry:
    def __init__(self, provider):
        self.provider = provider
    def get_provider(self, name):
        return self.provider

async def main():
    load_dotenv()
    store = InMemoryStore()
    context_builder = ContextBuilder()
    session_manager = SessionMemoryManager(store, context_builder)
    
    groq = GroqAdapter()
    registry = DummyRegistry(groq)
    
    pipeline = RuntimeExecutionPipeline(session_manager, registry)
    gateway = RuntimeGateway(pipeline)
    
    tools = [
        {
            "name": "get_stock_price",
            "description": "Gets the current price for a stock ticker.",
            "parameters": {
                "type": "object",
                "properties": { "ticker": { "type": "string" } },
                "required": ["ticker"]
            }
        }
    ]
    
    req = Request(
        id=str(uuid.uuid4()),
        session_id="test-session-126",
        payload={"text": "Can you tell me the stock price of Tesla?", "tools": tools}
    )
    
    print("Testing 'Can you tell me the stock price of Tesla?'")
    gen = gateway.submit_request_stream(req)
    
    item = await gen.asend(None)
    while True:
        try:
            if isinstance(item, dict) and item.get("type") == "tool_call":
                print(f"-> LLM requested Tool: {item['name']} with args: {item['arguments']}")
                
                # Simulate Tool Execution
                result = "The stock price of Tesla is $150.25."
                
                print(f"<- Returning Tool Result: {result}")
                
                # Let's peek into the memory context!
                context = await session_manager.build_context("test-session-126")
                import json
                print("CONTEXT BEFORE RESUMING:", json.dumps(context, indent=2))
                
                item = await gen.asend({"result": result})
            else:
                print(f"LLM Sentence: {item}")
                item = await gen.asend(None)
        except StopAsyncIteration:
            break

if __name__ == "__main__":
    asyncio.run(main())
