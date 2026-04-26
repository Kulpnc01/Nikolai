import asyncio
import logging

logger = logging.getLogger(__name__)

class SilicaStateMachine:
    STATES = {"IDLE", "SHOPPER_MODE", "NAVIGATION_MODE", "ERROR_MODE"}

    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.current_state = "IDLE"
        
        self.event_loop.subscribe("intent_prepare_shopper_module", self._to_shopper)
        self.event_loop.subscribe("AISLES_navigation_start", self._to_nav)
        self.event_loop.subscribe("system_error", self._to_error)
        self.event_loop.subscribe("return_to_idle", self._to_idle)

    async def _transition(self, new_state: str, payload: dict = None):
        if new_state in self.STATES and new_state != self.current_state:
            logger.info(f"[Silica State] {self.current_state} -> {new_state}")
            self.current_state = new_state
            await self.event_loop.publish("state_changed", {"state": new_state, "data": payload})

    async def _to_shopper(self, payload): await self._transition("SHOPPER_MODE", payload)
    async def _to_nav(self, payload): await self._transition("NAVIGATION_MODE", payload)
    async def _to_error(self, payload): await self._transition("ERROR_MODE", payload)
    async def _to_idle(self, payload): await self._transition("IDLE", payload)

