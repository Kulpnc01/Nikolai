# C:\Nikolai_0_3\nikolai.py

import sys
import asyncio
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Async Core Imports
from brain.core.async_context import AsyncContextManager
from brain.core.async_event_bridge import AsyncEventBridge
from brain.core.async_core_runtime import AsyncCoreRuntime
from brain.core.async_task_manager import AsyncTaskManager
from brain.core.async_respond_loop import AsyncRespondLoop

# Silica Imports
from brain.silica.event_loop import SilicaEventLoop
from brain.silica.pipeline_watcher import SilicaPipelineWatcher
from brain.silica.module_loader import SilicaModuleLoader
from brain.silica.state_machine import SilicaStateMachine
from brain.silica.node_coordinator import SilicaNodeCoordinator
from brain.silica.bridge_python import SilicaPythonBridge
from brain.silica.bridge_san import SilicaSANBridge

async def async_main() -> None:
    # 1. Setup Async Executive Layer
    ctx = AsyncContextManager(
        root_dir=ROOT,
        memory_dir=ROOT / "brain" / "memory",
        modules_dir=ROOT / "modules",
    )
    bridge = AsyncEventBridge()
    task_manager = AsyncTaskManager()
    runtime = AsyncCoreRuntime(ctx, bridge, task_manager)
    await runtime.initialize()

    # 2. Setup Silica Reflex Layer (Integrated in same Loop)
    silica_loop = SilicaEventLoop()
    
    # Initialize components
    watcher = SilicaPipelineWatcher(silica_loop, ROOT / "modules")
    loader = SilicaModuleLoader(silica_loop)
    state_machine = SilicaStateMachine(silica_loop)
    coordinator = SilicaNodeCoordinator(silica_loop)
    san_bridge = SilicaSANBridge(silica_loop)
    
    # Bridge Handshake
    # Silica talking to Python
    silica_python_bridge = SilicaPythonBridge(silica_loop, bridge.receive_from_silica)
    # Python talking to Silica
    bridge.bind_to_silica(silica_loop.publish)

    # 3. Schedule Background Tasks
    # All tasks run in the main asyncio loop
    asyncio.create_task(watcher.watch_loop())
    asyncio.create_task(san_bridge.start_grpc_server())
    asyncio.create_task(bridge.process_incoming())
    asyncio.create_task(silica_loop.start())

    print("[Nikolai 0.3] Online (Python 3.14) [Hybrid Async Core Active].")
    print("Type 'help' for commands, 'exit' to quit.\n")

    # 4. Start Respond Loop
    respond_loop = AsyncRespondLoop(runtime)
    await respond_loop.run()

    print("\n[Nikolai 0.3] Shutting down.")
    await task_manager.cancel_all()

if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass
