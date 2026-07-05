import sys
import os

# Add the backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from voxcore.configuration.loaders.config_loader import ConfigLoader
from voxcore.configuration.providers.env_provider import EnvProvider
from voxcore.configuration.resolution.config_resolver import ConfigResolver
from voxcore.configuration.validation.config_validator import ConfigValidator
from voxcore.configuration.lifecycle.config_manager import ConfigManager
from voxcore.observability.logging.structured_logger import StructuredLogger

def main():
    print("=== Testing Configuration ===")
    loader = ConfigLoader([EnvProvider()])
    resolver = ConfigResolver()
    validator = ConfigValidator()
    
    manager = ConfigManager(loader, resolver, validator)
    manager.initialize()
    
    config = manager.get_config()
    print(f"Loaded config environment: {config.app_env}")
    print(f"Loaded database URL: {config.database_url}")
    
    print("\n=== Testing Observability ===")
    logger = StructuredLogger("voxcore_smoke_test")
    logger.info("This is a test log!", test_key="test_value")
    
    try:
        raise ValueError("Oops!")
    except Exception as e:
        logger.error("We caught an error successfully.", error=e)

if __name__ == "__main__":
    main()
