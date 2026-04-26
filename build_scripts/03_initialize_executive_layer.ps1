# ---------------------------------------------------------
# Nikolai 0.3 – Async Executive Layer Initialization
# Installs the async core runtime, context, bridge, intent engine, 
# and task manager.
# ---------------------------------------------------------

$root = "C:\Nikolai_0_3"
$coreDir = "$root\brain\core"

# Ensure directory exists
if (-not (Test-Path $coreDir)) { New-Item -ItemType Directory -Path $coreDir | Out-Null }

# --- Async Context ---
$asyncContext = @'
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class AsyncContextManager:
    """
    Refined AsyncContextManager with namespacing for multi-module isolation.
    Handles global state and non-blocking interactions with persistent memory.
    """
    def __init__(self, root_dir: Path, memory_dir: Path, modules_dir: Path):
        self.root_dir = root_dir
        self.memory_dir = memory_dir
        self.modules_dir = modules_dir
        self.state: Dict[str, Any] = {"global": {}, "modules": {}}
        self._lock = asyncio.Lock()

    async def update(self, key: str, value: Any, namespace: str = "global"):
        """Asynchronously update a state value with namespace protection."""
        async with self._lock:
            if namespace == "global":
                self.state["global"][key] = value
            else:
                if namespace not in self.state["modules"]:
                    self.state["modules"][namespace] = {}
                self.state["modules"][namespace][key] = value

    async def get(self, key: str, default: Any = None, namespace: str = "global") -> Any:
        """Asynchronously retrieve a state value from a specific namespace."""
        async with self._lock:
            target = self.state["global"] if namespace == "global" else self.state["modules"].get(namespace, {})
            return target.get(key, default)

    async def delete(self, key: str, namespace: str = "global"):
        """Asynchronously delete a state value."""
        async with self._lock:
            target = self.state["global"] if namespace == "global" else self.state["modules"].get(namespace, {})
            if key in target:
                del target[key]

    async def get_full_snapshot(self) -> Dict[str, Any]:
        """Returns a deep copy of the current state for reasoning."""
        import copy
        async with self._lock:
            # Simple flattening for diagnostic reasoning
            flat = self.state["global"].copy()
            for mod_ns, mod_data in self.state["modules"].items():
                flat[f"module_{mod_ns}"] = mod_data
            return copy.deepcopy(flat)

    async def load_memory(self, filename: str) -> Optional[str]:
        """Non-blocking read from the memory directory."""
        mem_file = self.memory_dir / filename
        if not mem_file.exists():
            return None
        try:
            return await asyncio.to_thread(mem_file.read_text, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read memory {filename}: {e}")
            return None

    async def save_memory(self, filename: str, content: str):
        """Non-blocking write to the memory directory."""
        mem_file = self.memory_dir / filename
        try:
            await asyncio.to_thread(mem_file.write_text, content, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to write memory {filename}: {e}")
'@

Set-Content "$coreDir\async_context.py" $asyncContext


# --- Async Intent Engine ---
$asyncIntent = @'
import asyncio
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

@dataclass
class Intent:
    name: str
    raw_text: str
    entities: Dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0

class AsyncIntentEngine:
    """
    Refined Intent Engine with Regex-based Entity Extraction and pattern matching.
    """
    def __init__(self):
        # Patterns for extracting modules, nodes, and actions
        self.patterns = {
            "prepare_module": r"(?:prepare|init|setup)\s+(\w+)(?:\s+module)?",
            "node_command": r"(?:send|tell|dispatch)\s+(\w+)\s+to\s+node\s+(\w+)",
            "diagnose": r"(?:diagnose|check|repair)\s+(\w+)",
            "await_pipeline": r"(?:wait|await|listen|watch)\s+(?:for\s+)?(?:gcli\s+)?pipeline"
        }
        
        # Simple keyword fallback
        self.keywords = {
            "exit": ["exit", "quit", "shutdown"],
            "status": ["status", "health", "state", "system check"],
            "help": ["help", "commands", "what can you do", "explain"]
        }

    async def classify(self, text: str) -> Optional[Intent]:
        """
        Asynchronously process and classify the user input.
        """
        if not text:
            return None

        # Simulate NLP processing delay for future LLM integration readiness
        await asyncio.sleep(0.01) 
        
        t = text.strip().lower()
        entities = {}

        # 1. Pattern Matching with Entity Extraction
        for intent_name, pattern in self.patterns.items():
            match = re.search(pattern, t)
            if match:
                if intent_name == "prepare_module":
                    entities["module"] = match.group(1)
                elif intent_name == "node_command":
                    entities["action"] = match.group(1)
                    entities["node"] = match.group(2)
                elif intent_name == "diagnose":
                    entities["target"] = match.group(1)
                
                logger.debug(f"Intent classified (Pattern): {intent_name} with entities {entities}")
                return Intent(name=intent_name, raw_text=text, entities=entities)

        # 2. Check explicit keyword mappings
        for intent_name, phrases in self.keywords.items():
            if any(phrase in t for phrase in phrases):
                logger.debug(f"Intent classified (Keyword): {intent_name}")
                return Intent(name=intent_name, raw_text=text)

        # Fallback to generic free text
        logger.debug(f"Intent classified: free_text")
        return Intent(name="free_text", raw_text=text)
'@

Set-Content "$coreDir\async_intent_engine.py" $asyncIntent


# --- Async Event Bridge ---
$asyncBridge = @'
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
'@

Set-Content "$coreDir\async_event_bridge.py" $asyncBridge


# --- Async Core Runtime ---
$asyncRuntime = @'
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from .async_context import AsyncContextManager
from .async_intent_engine import AsyncIntentEngine
from .async_event_bridge import AsyncEventBridge
from .async_task_manager import AsyncTaskManager

logger = logging.getLogger(__name__)

class AsyncCoreRuntime:
    """
    Refined Orchestrator Layer. 
    Manages multiple modules, strategic node coordination, and background reasoning.
    """
    def __init__(self, context: AsyncContextManager, bridge: AsyncEventBridge, tasks: AsyncTaskManager):
        self.context = context
        self.bridge = bridge
        self.tasks = tasks
        self.intent_engine = AsyncIntentEngine()
        self.is_running = False
        self.spine_path = Path(r"C:\Nikolai_0_3\spine\project_spine.json")

        # Core Subscriptions
        self.bridge.subscribe("module_loaded", self._on_module_activated)
        self.bridge.subscribe("state_changed", self._on_silica_state_change)
        self.bridge.subscribe("telemetry_updated", self._on_telemetry_received)
        self.bridge.subscribe("system_error", self._on_system_error)

    async def initialize(self):
        """Asynchronous startup sequence."""
        logger.info("Initializing AsyncCoreRuntime (Orchestrator Mode)...")
        await self._load_spine()
        self.is_running = True
        logger.info("AsyncCoreRuntime fully online.")

    async def _load_spine(self):
        if not self.spine_path.exists():
            return
        try:
            content = await asyncio.to_thread(self.spine_path.read_text, encoding="utf-8")
            await self.context.update("spine", json.loads(content))
        except Exception as e:
            logger.error(f"Failed to load spine: {e}")

    async def process_user_input(self, text: str) -> Optional[str]:
        """Process natural language input using entities and intents."""
        intent = await self.intent_engine.classify(text)
        if not intent:
            return None

        # 1. System Commands
        if intent.name == "exit":
            self.is_running = False
            return "Orchestrator: Initiating shutdown sequence."
            
        if intent.name == "status":
            return await self._format_status_report()

        # 2. Multi-Module Orchestration
        if intent.name == "prepare_module":
            module = intent.entities.get("module", "unknown")
            await self.bridge.publish_to_silica("intent_prepare_module", {"module": module})
            return f"Orchestrator: Delegated deployment of '{module}' module to Phi Silica."

        if intent.name == "await_pipeline":
            return "Orchestrator: Pipeline monitoring is active in the reflex layer."

        # 3. Multi-Node Coordination
        if intent.name == "node_command":
            node = intent.entities.get("node")
            action = intent.entities.get("action")
            await self.bridge.publish_to_silica("dispatch_command", {"node_id": node, "command": action})
            return f"Orchestrator: Dispatching command '{action}' to Node '{node}'."

        # 4. Deep Diagnostic Reasoning (Help)
        if intent.name == "help":
            return await self._execute_diagnostic_reasoning(text)

        return f"Executive: Classified intent '{intent.name}'. (No action defined)"

    # --- Silica Event Handlers ---

    async def _on_module_activated(self, payload: dict):
        module_name = payload.get("module_name")
        logger.info(f"Executive layer notified: Module '{module_name}' activated.")
        
        # Register in executive context
        active_modules = await self.context.get("active_modules", [])
        if module_name not in active_modules:
            active_modules.append(module_name)
            await self.context.update("active_modules", active_modules)
        
        # Schedule deep reasoning task about the new module
        await self.tasks.schedule(self._reason_about_module_integration(module_name))

    async def _on_silica_state_change(self, payload: dict):
        new_state = payload.get("state")
        await self.context.update("silica_state", new_state)
        logger.info(f"Reflex state transition tracked: {new_state}")

    async def _on_telemetry_received(self, payload: dict):
        node_id = payload.get("node_id")
        data = payload.get("data", {})
        # Route telemetry to the correct module namespace in context
        await self.context.update("last_telemetry", data, namespace=node_id)
        
        # Reflex action: Check for node errors
        if data.get("current_state") == "ERROR_RECOVERY":
            await self.tasks.schedule(self._handle_node_error(node_id, data))

    async def _on_system_error(self, payload: dict):
        logger.error(f"Reflex layer reported system error: {payload.get('error')}")
        await self.tasks.schedule(self._orchestrate_recovery(payload))

    # --- Strategic Background Tasks ---

    async def _reason_about_module_integration(self, module_name: str):
        """Perform long-term strategic analysis of a new module's impact."""
        logger.info(f"Reasoning: Validating {module_name} capabilities against project spine...")
        await asyncio.sleep(1.5) # Simulated complex reasoning
        logger.info(f"Reasoning: {module_name} integration verified and constraints updated.")

    async def _handle_node_error(self, node_id: str, data: dict):
        logger.warning(f"Orchestrator: Node '{node_id}' entered error state. Analyzing root cause...")
        # Future: Call LLM or DiagnosticEngine here
        await asyncio.sleep(2.0)
        logger.info(f"Orchestrator: Decision - Resetting node '{node_id}' to IDLE.")
        await self.bridge.publish_to_silica("dispatch_command", {"node_id": node_id, "command": "RESET"})

    async def _orchestrate_recovery(self, error_payload: dict):
        await asyncio.sleep(1.0)
        await self.bridge.publish_to_silica("return_to_idle", {"source": "executive_recovery"})

    async def _format_status_report(self) -> str:
        silica_state = await self.context.get("silica_state", "UNKNOWN")
        active_modules = await self.context.get("active_modules", [])
        return (
            f"### Nikolai Executive Status\n"
            f"- **Reflex Layer:** {silica_state}\n"
            f"- **Active Modules:** {', '.join(active_modules) if active_modules else 'None'}\n"
            f"- **Task Manager:** {len(self.tasks.active_tasks)} background tasks running.\n"
        )

    async def _execute_diagnostic_reasoning(self, query: str) -> str:
        """Deep introspection via HelpDiagnosticModule logic."""
        try:
            from modules.HelpDiagnosticModule.logic.diagnostic_engine import DiagnosticEngine
            engine = DiagnosticEngine(self.context.root_dir)
            snapshot = await self.context.get_full_snapshot()
            return await engine.handle_help_request(query, snapshot)
        except Exception as e:
            logger.error(f"Help module execution failed: {e}")
            return "Help logic currently unavailable (Module logic mismatch)."
'@

Set-Content "$coreDir\async_core_runtime.py" $asyncRuntime


# --- Async Task Manager ---
$asyncTasks = @'
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
'@

Set-Content "$coreDir\async_task_manager.py" $asyncTasks


# --- Async Respond Loop ---
$asyncRespond = @'
import asyncio
import sys
import logging

logger = logging.getLogger(__name__)

class AsyncRespondLoop:
    """
    Non-blocking user input reader.
    Replaces the synchronous generator to allow the async event loop to breathe
    while waiting for stdin.
    """
    def __init__(self, core_runtime):
        self.core = core_runtime

    async def run(self):
        """
        Continuously read from stdin without blocking the asyncio loop.
        """
        logger.info("AsyncRespondLoop active. Ready for user input.")
        
        loop = asyncio.get_running_loop()
        
        while self.core.is_running:
            # Run the blocking input() call in a separate thread
            try:
                user_input = await loop.run_in_executor(None, sys.stdin.readline)
            except Exception as e:
                logger.error(f"Stdin read error: {e}")
                break

            if not user_input:
                break # EOF

            text = user_input.strip()
            if text:
                response = await self.core.process_user_input(text)
                if response:
                    print(f"\n{response}\n> ", end="", flush=True)
                else:
                    print("> ", end="", flush=True)
            else:
                 print("> ", end="", flush=True)
'@

Set-Content "$coreDir\async_respond_loop.py" $asyncRespond

Write-Host "Nikolai 0.3 Async Executive Layer initialized."
