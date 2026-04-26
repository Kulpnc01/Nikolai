import asyncio
import logging

logger = logging.getLogger(__name__)

class SilicaPythonBridge:
    def __init__(self, event_loop, receive_from_silica_func):
        self.event_loop = event_loop
        self.receive_from_silica_func = receive_from_silica_func
        
        self.event_loop.subscribe("module_loaded", self._notify_executive)
        self.event_loop.subscribe("state_changed", self._notify_executive)

    async def _notify_executive(self, payload: dict):
        if self.receive_from_silica_func:
            # We need to find the current event type from the context or pass it
            # For simplicity, we'll assume the payload or a wrapper carries it
            event_type = "module_loaded" if "module_name" in payload else "state_changed"
            await self.receive_from_silica_func(event_type, payload)
