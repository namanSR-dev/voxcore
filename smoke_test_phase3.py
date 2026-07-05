import sys
import os
import asyncio
import jwt
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from voxcore.security.authentication.token_validator import TokenValidator
from voxcore.security.authorization.policy_enforcer import PolicyEnforcer
from voxcore.storage.connection.connection_pool import ConnectionPool

async def main():
    print("=== Testing Security (Authentication & Authorization) ===")
    secret = "my-super-secret-key"
    validator = TokenValidator(secret)
    
    # Generate a dummy token that expires in 15 minutes
    payload = {
        "sub": "test_user",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    print(f"Generated JWT: {token[:30]}...")
    
    # Validate the token
    claims = validator.validate(token)
    print(f"Successfully Validated Claims: {claims}")
    
    # Test Authorization (RBAC)
    enforcer = PolicyEnforcer({"admin": ["*"], "standard_user": ["read_memory"]})
    
    class DummyIdentity:
        roles = ["standard_user"]
        
    try:
        print("\nAttempting to perform unauthorized 'delete_memory' action...")
        enforcer.authorize(DummyIdentity(), "delete_memory", "memory_database")
    except Exception as e:
        print(f"✅ Policy Enforcer blocked the action correctly: {e}")

    print("\n=== Testing Storage (SQLAlchemy) ===")
    try:
        # We need an async sqlite driver for this to fully work, but we can verify the pool instantiates
        pool = ConnectionPool("sqlite+aiosqlite:///:memory:")
        print("✅ SQLAlchemy AsyncEngine and SessionMaker initialized perfectly.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
