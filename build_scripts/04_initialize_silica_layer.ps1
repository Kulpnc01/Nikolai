# ---------------------------------------------------------
# Nikolai 0.3 – Phi Silica Reflex Layer Initialization
# Installs the event loop, pipeline watcher, module loader, 
# state machine, and coordinators.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"
$silicaDir = "$root\brain\silica"

# Ensure directory exists
if (-not (Test-Path $silicaDir)) { New-Item -ItemType Directory -Path $silicaDir | Out-Null }

# --- Silica Event Loop ---
$eventLoop = @'
import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class SilicaEventLoop:
    """
    Central async event bus for the Phi Silica layer.
    """
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
'@

Set-Content "$silicaDir\event_loop.py" $eventLoop


# --- Silica Pipeline Watcher ---
$pipelineWatcher = @'
import asyncio
from pathlib import Path
import logging
from typing import Set

logger = logging.getLogger(__name__)

class SilicaPipelineWatcher:
    def __init__(self, event_loop, modules_dir: Path):
        self.event_loop = event_loop
        self.modules_dir = modules_dir
        self.expected_artifacts = {
            "san_build_spec.txt",
            "san_final_spec.txt",
            "shopper_assistant_node_san.zip",
            "module_contract.json",
        }
        self.known_modules: Set[str] = set()

    async def watch_loop(self, poll_interval: float = 2.0):
        logger.info(f"Silica Pipeline Watcher monitoring: {self.modules_dir}")
        while True:
            if self.modules_dir.exists():
                for module_path in self.modules_dir.iterdir():
                    if module_path.is_dir() and module_path.name not in self.known_modules:
                        incoming = module_path / "pipeline" / "incoming"
                        if incoming.exists():
                            present = {p.name for p in incoming.iterdir() if p.is_file()}
                            if self.expected_artifacts.issubset(present):
                                logger.info(f"Artifacts detected for module: {module_path.name}")
                                self.known_modules.add(module_path.name)
                                await self.event_loop.publish("module_artifacts_ready", {
                                    "module_name": module_path.name, 
                                    "path": module_path
                                })
            await asyncio.sleep(poll_interval)
'@

Set-Content "$silicaDir\pipeline_watcher.py" $pipelineWatcher


# --- Silica Module Loader ---
$moduleLoader = @'
import asyncio
import json
import zipfile
from pathlib import Path
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SilicaModuleLoader:
    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.loaded_modules: Dict[str, Any] = {}
        self.event_loop.subscribe("module_artifacts_ready", self.handle_artifacts_ready)

    async def handle_artifacts_ready(self, payload: dict):
        module_name = payload["module_name"]
        module_path: Path = payload["path"]
        logger.info(f"Silica Module Loader verifying: {module_name}")
        
        success = await asyncio.to_thread(self._unpack_and_validate, module_path)
        
        if success:
            contract_path = module_path / "pipeline" / "incoming" / "module_contract.json"
            try:
                with open(contract_path, "r") as f:
                    contract = json.load(f)
                
                self.loaded_modules[module_name] = {
                    "path": str(module_path),
                    "contract": contract,
                    "status": "active"
                }
                logger.info(f"Module {module_name} activated successfully.")
                await self.event_loop.publish("module_loaded", {
                    "module_name": module_name, 
                    "contract": contract
                })
            except Exception as e:
                logger.error(f"Contract parsing failed for {module_name}: {e}")
                await self.event_loop.publish("module_error", {"module": module_name, "error": str(e)})

    def _unpack_and_validate(self, module_path: Path) -> bool:
        incoming = module_path / "pipeline" / "incoming"
        zip_path = incoming / "shopper_assistant_node_san.zip"
        extract_dir = module_path / "android_app"
        
        try:
            if zip_path.exists() and zipfile.is_zipfile(zip_path):
                extract_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                return True
        except Exception as e:
            logger.error(f"Failed to unpack {zip_path}: {e}")
        return False
'@

Set-Content "$silicaDir\module_loader.py" $moduleLoader


# --- Silica State Machine ---
$stateMachine = @'
import asyncio
import logging

logger = logging.getLogger(__name__)

class SilicaStateMachine:
    STATES = {"IDLE", "SHOPPER_MODE", "NAVIGATION_MODE", "ERROR_MODE"}

    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.current_state = "IDLE"
        
        self.event_loop.subscribe("intent_prepare_shopper_module", self._to_shopper)
        self.event_loop.subscribe("san_navigation_start", self._to_nav)
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
'@

Set-Content "$silicaDir\state_machine.py" $stateMachine


# --- Silica Node Coordinator ---
$nodeCoordinator = @'
import asyncio
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class SilicaNodeCoordinator:
    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.active_nodes: Dict[str, dict] = {}
        
        self.event_loop.subscribe("san_telemetry_received", self.handle_telemetry)
        self.event_loop.subscribe("dispatch_command", self.dispatch_command)

    async def register_node(self, node_id: str, capabilities: list):
        self.active_nodes[node_id] = {"status": "online", "capabilities": capabilities}
        logger.info(f"[Node Coordinator] SAN Node registered: {node_id}")
        await self.event_loop.publish("node_registered", {"node_id": node_id})

    async def handle_telemetry(self, payload: dict):
        node_id = payload.get("node_id")
        data = payload.get("data", {})
        if data.get("current_state") == "STORE_NAVIGATION":
             await self.event_loop.publish("san_navigation_start", payload)
        await self.event_loop.publish("telemetry_updated", payload)

    async def dispatch_command(self, payload: dict):
        node_id = payload.get("node_id")
        command = payload.get("command")
        if node_id in self.active_nodes:
            await self.event_loop.publish("bridge_san_send", payload)
        else:
            logger.warning(f"Dispatch failed: Node {node_id} offline or unknown.")
'@

Set-Content "$silicaDir\node_coordinator.py" $nodeCoordinator


# --- Silica Python Bridge ---
$pythonBridge = @'
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
            event_type = "module_loaded" if "module_name" in payload else "state_changed"
            await self.receive_from_silica_func(event_type, payload)

    async def receive_intent_from_core(self, intent_name: str, raw_text: str):
        logger.info(f"Silica received intent from Executive Layer: {intent_name}")
        await self.event_loop.publish(f"intent_{intent_name}", {"raw_text": raw_text})
'@

Set-Content "$silicaDir\bridge_python.py" $pythonBridge


# --- Silica SAN Bridge ---
$sanBridge = @'
import asyncio
import logging
import grpc
from pathlib import Path
import sys

# Add proto directory to path for imports
PROTO_PATH = str(Path(__file__).parent / "proto")
if PROTO_PATH not in sys.path:
    sys.path.append(PROTO_PATH)

import san_protocol_pb2
import san_protocol_pb2_grpc

logger = logging.getLogger(__name__)

class ShopperAssistantNodeServicer(san_protocol_pb2_grpc.ShopperAssistantNodeServicer):
    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.command_queues = {} # node_id -> asyncio.Queue

    async def StreamTelemetry(self, request_iterator, context):
        async for request in request_iterator:
            logger.debug(f"[SAN Telemetry] Received from {request.node_id}: {request.current_state}")
            payload = {
                "node_id": request.node_id,
                "data": {
                    "current_state": request.current_state,
                    "payload_json": request.payload_json,
                    "timestamp": request.timestamp
                }
            }
            await self.event_loop.publish("san_telemetry_received", payload)
        return san_protocol_pb2.TelemetryResponse(success=True)

    async def StreamCommands(self, request, context):
        node_id = request.node_id
        if node_id not in self.command_queues:
            self.command_queues[node_id] = asyncio.Queue()
        
        logger.info(f"[SAN Bridge] Command stream established for node: {node_id}")
        
        while True:
            try:
                command_payload = await self.command_queues[node_id].get()
                yield san_protocol_pb2.CommandResponse(
                    command_id=command_payload.get("command_id", "cmd_0"),
                    action=command_payload.get("action", ""),
                    parameters_json=command_payload.get("parameters_json", "{}")
                )
            except asyncio.CancelledError:
                logger.info(f"[SAN Bridge] Command stream closed for node: {node_id}")
                break

class SilicaSANBridge:
    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.servicer = ShopperAssistantNodeServicer(event_loop)
        self.server = None
        self.event_loop.subscribe("bridge_san_send", self._queue_command_for_san)

    async def start_grpc_server(self, port: int = 50051):
        self.server = grpc.aio.server()
        san_protocol_pb2_grpc.add_ShopperAssistantNodeServicer_to_server(self.servicer, self.server)
        listen_addr = f"[::]:{port}"
        self.server.add_insecure_port(listen_addr)
        logger.info(f"[SAN Bridge] Starting async gRPC server on {listen_addr}")
        await self.server.start()
        await self.server.wait_for_termination()

    async def _queue_command_for_san(self, payload: dict):
        node_id = payload.get("node_id")
        if not node_id: return
        if node_id not in self.servicer.command_queues:
            self.servicer.command_queues[node_id] = asyncio.Queue()
        await self.servicer.command_queues[node_id].put(payload)
'@

Set-Content "$silicaDir\bridge_san.py" $sanBridge

Write-Host "Nikolai 0.3 Phi Silica Reflex Layer initialized."
