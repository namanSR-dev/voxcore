"""
runtime/events/event_bus.py

Provides internal pub/sub capabilities to decouple VoxCore subsystems.
"""
from typing import Any, Callable, Dict, List
import asyncio

class EventBus:
    """
    Dispatches domain events (e.g., RequestStarted, MemoryIndexed) to registered listeners.
    """
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Registers a callback for a specific event type.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event: Any) -> None:
        """
        Broadcasts an event asynchronously to all registered subscribers.
        """
        event_type = type(event).__name__
        await self._notify_subscribers(event_type, event)

    async def _notify_subscribers(self, event_type: str, event: Any) -> None:
        handlers = self._subscribers.get(event_type, [])
        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(asyncio.create_task(handler(event)))
            else:
                # Simple synchronous execution (in production we might run this in executor)
                handler(event)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
