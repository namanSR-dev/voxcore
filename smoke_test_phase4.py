import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from voxcore.tools.sandbox.execution_sandbox import ExecutionSandbox
from voxcore.providers.normalization.output_normalizer import OutputNormalizer

async def main():
    print("=== Testing Tools Sandbox ===")
    # We set a strict 2-second timeout for our test
    sandbox = ExecutionSandbox(timeout_seconds=2)
    
    # 1. Test a safe fast function
    def fast_function(x):
        return x * 2
        
    result = await sandbox.run_safely(fast_function, 10)
    print(f"✅ Fast function result: {result}")
    
    # 2. Test an evil slow function that tries to block the thread
    def slow_function():
        time.sleep(10) # Simulating a tool that hangs indefinitely
        return "I finished!"
        
    try:
        print("Running a slow function (Should timeout after 2 seconds)...")
        await sandbox.run_safely(slow_function)
    except Exception as e:
        print(f"✅ Sandbox caught the slow function: {e}")
        
    print("\n=== Testing Provider Normalization ===")
    normalizer = OutputNormalizer()
    
    # Fake raw responses from the external APIs
    openai_raw = {
        "id": "chatcmpl-123",
        "choices": [{"message": {"content": "Hello from OpenAI!"}}]
    }
    
    ollama_raw = {
        "message": {"content": "Hello from Ollama!"}
    }
    
    openai_res = normalizer.normalize(openai_raw, "openai")
    ollama_res = normalizer.normalize(ollama_raw, "ollama")
    
    print(f"✅ OpenAI Normalized: {openai_res.output['text']}")
    print(f"✅ Ollama Normalized: {ollama_res.output['text']}")

if __name__ == "__main__":
    asyncio.run(main())
