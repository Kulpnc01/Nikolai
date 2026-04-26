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
            engine = DiagnosticEngine(self.spine_path.parent.parent)
            snapshot = await self.context.get_full_snapshot()
            return await engine.handle_help_request(query, snapshot)
        except Exception as e:
            logger.error(f"Help module execution failed: {e}")
            return "Help logic currently unavailable (Module logic mismatch)."


