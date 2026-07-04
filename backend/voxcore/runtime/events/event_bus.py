"""
runtime/events/event_bus.py

Provides internal pub/sub capabilities to decouple VoxCore subsystems.
"""
from typing import Any, Callable

class EventBus:
    """
    Dispatches domain events (e.g., RequestStarted, MemoryIndexed) to registered listeners.
    """
    def __init__(self) -> None:
        pass

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Registers a callback for a specific event type.
        """
        pass

    async def publish(self, event: Any) -> None:
        """
        Broadcasts an event asynchronously to all registered subscribers.
        """
        pass

    async def _notify_subscribers(self, event: Any) -> None:
        pass
