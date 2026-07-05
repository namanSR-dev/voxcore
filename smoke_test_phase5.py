import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from voxcore.runtime.events.event_bus import EventBus
from voxcore.runtime.scheduler.task_queue import TaskQueue
from voxcore.runtime.kernel.bootstrapper import Bootstrapper

async def main():
    print("=== Testing Runtime Subsystems ===")
    
    # 1. Test Event Bus (Pub/Sub)
    bus = EventBus()
    
    class SystemStartedEvent:
        pass
        
    def on_system_started(event):
        print("✅ Event Bus correctly routed SystemStartedEvent!")
        
    bus.subscribe("SystemStartedEvent", on_system_started)
    await bus.publish(SystemStartedEvent())
    
    # 2. Test Task Queue (Background Jobs)
    queue = TaskQueue(worker_count=1)
    queue.start()
    
    def background_job():
        print("✅ Background Task Queue successfully processed a job on a separate thread!")
        
    task_id = await queue.enqueue(background_job)
    
    # Give the background worker a tiny fraction of a second to process the queue
    await asyncio.sleep(0.1)
    status = await queue.get_status(task_id)
    print(f"✅ Background Task Status: {status}")
    
    # Clean up the background workers
    for worker in queue._workers:
        worker.cancel()
        
    # 3. Test Bootstrapper
    boot = Bootstrapper()
    print("\n=== Simulating Application Boot ===")
    boot.boot()
    boot.shutdown()
    
if __name__ == "__main__":
    asyncio.run(main())
