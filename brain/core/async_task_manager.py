import asyncio
import logging
from typing import Coroutine

logger = logging.getLogger(__name__)

class AsyncTaskManager:
    """
    Manages long-running background tasks for the executive layer.
    Ensures tasks don't block the main reasoning loop and handles their lifecycle.
    """
    def __init__(self):
        self.active_tasks = set()

    async def schedule(self, coro: Coroutine, name: str = None) -> asyncio.Task:
        """Schedule a coroutine to run in the background."""
        task = asyncio.create_task(coro, name=name)
        self.active_tasks.add(task)
        task.add_done_callback(self.active_tasks.discard)
        logger.debug(f"Scheduled background task: {task.get_name()}")
        return task

    async def cancel_all(self):
        """Cancel all running background tasks (e.g., during shutdown)."""
        for task in self.active_tasks:
            if not task.done():
                task.cancel()
        
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
        logger.info("All executive background tasks cancelled.")
