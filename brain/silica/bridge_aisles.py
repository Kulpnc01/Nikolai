import asyncio
import logging
import grpc
from pathlib import Path
import sys

# Add proto directory to path for imports
PROTO_PATH = str(Path(__file__).parent / "proto")
if PROTO_PATH not in sys.path:
    sys.path.append(PROTO_PATH)

import AISLES_protocol_pb2
import AISLES_protocol_pb2_grpc

logger = logging.getLogger(__name__)

class AISLESNodeServicer(AISLES_protocol_pb2_grpc.AISLESNodeServicer):
    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.command_queues = {} # node_id -> asyncio.Queue

    async def StreamTelemetry(self, request_iterator, context):
        async for request in request_iterator:
            logger.debug(f"[AISLES Telemetry] Received from {request.node_id}: {request.current_state}")
            payload = {
                "node_id": request.node_id,
                "data": {
                    "current_state": request.current_state,
                    "payload_json": request.payload_json,
                    "timestamp": request.timestamp
                }
            }
            await self.event_loop.publish("AISLES_telemetry_received", payload)
        return AISLES_protocol_pb2.TelemetryResponse(success=True)

    async def StreamCommands(self, request, context):
        node_id = request.node_id
        if node_id not in self.command_queues:
            self.command_queues[node_id] = asyncio.Queue()
        
        logger.info(f"[AISLES Bridge] Command stream established for node: {node_id}")
        
        while True:
            try:
                # Wait for commands from the event loop
                command_payload = await self.command_queues[node_id].get()
                yield AISLES_protocol_pb2.CommandResponse(
                    command_id=command_payload.get("command_id", "cmd_0"),
                    action=command_payload.get("action", ""),
                    parameters_json=command_payload.get("parameters_json", "{}")
                )
            except asyncio.CancelledError:
                logger.info(f"[AISLES Bridge] Command stream closed for node: {node_id}")
                break

class SilicaAISLESBridge:
    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.servicer = AISLESNodeServicer(event_loop)
        self.server = None
        
        # Subscribe to outgoing commands
        self.event_loop.subscribe("bridge_AISLES_send", self._queue_command_for_AISLES)

    async def start_grpc_server(self, port: int = 50051):
        self.server = grpc.aio.server()
        AISLES_protocol_pb2_grpc.add_AISLESNodeServicer_to_server(self.servicer, self.server)
        
        listen_addr = f"[::]:{port}"
        self.server.add_insecure_port(listen_addr)
        
        logger.info(f"[AISLES Bridge] Starting async gRPC server on {listen_addr}")
        await self.server.start()
        # Keep server running until task is cancelled
        await self.server.wait_for_termination()

    async def _queue_command_for_AISLES(self, payload: dict):
        node_id = payload.get("node_id")
        if not node_id:
            logger.warning("[AISLES Bridge] Received command with no node_id")
            return

        if node_id not in self.servicer.command_queues:
            self.servicer.command_queues[node_id] = asyncio.Queue()
        
        logger.debug(f"[AISLES Bridge] Queuing command for {node_id}")
        await self.servicer.command_queues[node_id].put(payload)

