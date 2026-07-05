"""
runtime/scheduler/task_queue.py

Manages background jobs such as memory summarization or event dispatching.
"""
from typing import Any, Dict, List
import asyncio
import uuid

class TaskQueue:
    """
    A lightweight, in-memory queue for scheduling background tasks.
    """
    def __init__(self, worker_count: int = 1) -> None:
        self.worker_count = worker_count
        self._queue: asyncio.Queue = asyncio.Queue()
        self._status: Dict[str, str] = {}
        self._workers: List[asyncio.Task] = []

    def start(self) -> None:
        for _ in range(self.worker_count):
            task = asyncio.create_task(self._worker_loop())
            self._workers.append(task)

    async def enqueue(self, task_func: Any, *args: Any, **kwargs: Any) -> str:
        """
        Submits a task for background execution and returns a Tracking ID.
        """
        task_id = str(uuid.uuid4())
        self._status[task_id] = "queued"
        await self._queue.put((task_id, task_func, args, kwargs))
        return task_id

    async def get_status(self, task_id: str) -> str:
        """
        Queries the current status of a queued task.
        """
        if task_id not in self._status:
            raise ValueError("Task ID not found")
        return self._status[task_id]

    async def _worker_loop(self) -> None:
        while True:
            try:
                task_id, task_func, args, kwargs = await self._queue.get()
                self._status[task_id] = "running"
                
                try:
                    if asyncio.iscoroutinefunction(task_func):
                        await task_func(*args, **kwargs)
                    else:
                        task_func(*args, **kwargs)
                    self._status[task_id] = "completed"
                except Exception as e:
                    self._status[task_id] = f"failed: {str(e)}"
                finally:
                    self._queue.task_done()
            except asyncio.CancelledError:
                break
