"""
transport/http/router.py

Defines URL paths and maps them to VoxCore API controllers.
"""
from typing import Any

class HttpRouter:
    """
    Connects incoming framework HTTP requests to the framework-agnostic API controllers.
    """
    def __init__(self, api_controller: Any) -> None:
        pass

    def register_routes(self, app: Any) -> None:
        """
        Registers all GET/POST endpoints onto the provided web application instance.
        """
        pass
