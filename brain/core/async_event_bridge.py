import asyncio
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

class AsyncEventBridge:
    """
    Asynchronous message passing bridge between the Python Executive layer and the Phi Silica Reflex layer.
    """
    def __init__(self):
        self.executive_subscribers: Dict[str, List[Callable]] = {}
        # Queue for incoming events from Silica
        self.incoming_queue = asyncio.Queue()
        # Reference to Silica's publish method (injected during startup)
        self.silica_publish_func = None 

    def bind_to_silica(self, silica_publish: Callable):
        """Connect the bridge to Silica's event bus."""
        self.silica_publish_func = silica_publish

    def subscribe(self, event_type: str, callback: Callable):
        """Register executive-layer callbacks for specific events."""
        if event_type not in self.executive_subscribers:
            self.executive_subscribers[event_type] = []
        self.executive_subscribers[event_type].append(callback)

    async def publish_to_silica(self, event_type: str, payload: Any = None):
        """Push an event down to the Silica reflex layer."""
        if self.silica_publish_func:
            logger.debug(f"[Bridge -> Silica] {event_type}")
            await self.silica_publish_func(event_type, payload)
        else:
            logger.warning("Cannot publish to Silica: Bridge not bound.")

    async def receive_from_silica(self, event_type: str, payload: Any = None):
        """Called by Silica to push events up to the Executive layer."""
        logger.debug(f"[Silica -> Bridge] {event_type}")
        await self.incoming_queue.put((event_type, payload))

    async def process_incoming(self):
        """Continuous loop processing events arriving from Silica."""
        logger.info("AsyncEventBridge incoming processor started.")
        while True:
            event_type, payload = await self.incoming_queue.get()
            if event_type in self.executive_subscribers:
                for callback in self.executive_subscribers[event_type]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            asyncio.create_task(callback(payload))
                        else:
                            callback(payload)
                    except Exception as e:
                        logger.error(f"Error executing callback for {event_type}: {e}")
            self.incoming_queue.task_done()
