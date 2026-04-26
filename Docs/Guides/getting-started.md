# Getting Started with Nikolai 0.3

Nikolai 0.3 is a hybrid asynchronous cognitive engine designed for low-latency coordination between high-level reasoning and edge-node execution.

## 1. Environment Requirements
- **Python:** 3.12+ (Python 3.14 recommended for optimized async execution).
- **PowerShell:** PowerShell Core (pwsh) for system orchestration.
- **Tailscale:** Required for secure communication with Shopper Assistant Nodes (AISLES).

## 2. Launching the System
Nikolai is launched via the PowerShell system entry point, which anchors the architectural context.

```powershell
# From the project root
./nikolai.ps1
```

Once online, you will see the hybrid async core active.

## 3. Basic Commands
- `help`: Access the deep reasoning diagnostic engine.
- `status`: View the state of the reflex and executive layers.
- `prepare module <name>`: Initiate the deployment pipeline for a new module (e.g., `shopper`).
- `exit`: Gracefully shutdown all async loops and background tasks.

## 4. Understanding the Layers
- **Executive Layer (The Slow Brain):** Handles your intents, plans, and memory.
- **Reflex Layer (The Fast Brain):** Watches for incoming files and manages live node connections (gRPC).

