import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from fastapi.testclient import TestClient
from voxcore.main import app

client = TestClient(app)

def main():
    print("=== Testing API Controllers & Schema Validation ===")
    
    # 1. Test the Health Check endpoint
    response = client.get("/health")
    print(f"✅ Health Check successful: {response.json()}")
    
    # 2. Test the Schema Validator blocking an invalid payload
    print("\nSending an invalid payload (missing the required 'prompt' field)...")
    invalid_payload = {"stream": False}
    response = client.post("/v1/inference", json=invalid_payload)
    print(f"✅ Schema Validator correctly blocked the request: {response.json()}")
    
    # 3. Test a successful end-to-end flow through the HTTP Controller -> Gateway -> Pipeline
    print("\nSending a valid prompt payload...")
    valid_payload = {"prompt": "Hello VoxCore, what is your name?"}
    response = client.post("/v1/inference", json=valid_payload)
    print(f"✅ Successful Response from Runtime: {response.json()}")

if __name__ == "__main__":
    main()
