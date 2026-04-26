import asyncio
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class SilicaNodeCoordinator:
    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.active_nodes: Dict[str, dict] = {}
        
        self.event_loop.subscribe("AISLES_telemetry_received", self.handle_telemetry)
        self.event_loop.subscribe("dispatch_command", self.dispatch_command)

    async def register_node(self, node_id: str, capabilities: list):
        self.active_nodes[node_id] = {"status": "online", "capabilities": capabilities}
        logger.info(f"[Node Coordinator] AISLES Node registered: {node_id}")
        await self.event_loop.publish("node_registered", {"node_id": node_id})

    async def handle_telemetry(self, payload: dict):
        node_id = payload.get("node_id")
        data = payload.get("data", {})
        if data.get("current_state") == "STORE_NAVIGATION":
             await self.event_loop.publish("AISLES_navigation_start", payload)
        await self.event_loop.publish("telemetry_updated", payload)

    async def dispatch_command(self, payload: dict):
        node_id = payload.get("node_id")
        command = payload.get("command")
        if node_id in self.active_nodes:
            await self.event_loop.publish("bridge_AISLES_send", payload)
        else:
            logger.warning(f"Dispatch failed: Node {node_id} offline or unknown.")

