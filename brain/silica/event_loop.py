import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class SilicaEventLoop:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.loop = asyncio.get_event_loop()
        self.tasks: List[asyncio.Task] = []

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def publish(self, event_type: str, payload: Any = None):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    self.tasks.append(asyncio.create_task(callback(payload)))
                else:
                    self.loop.call_soon(callback, payload)

    def run_task(self, coro):
        task = self.loop.create_task(coro)
        self.tasks.append(task)
        return task

    async def start(self):
        logger.info("Phi Silica Event Loop activated.")
        while True:
            await asyncio.sleep(3600)
