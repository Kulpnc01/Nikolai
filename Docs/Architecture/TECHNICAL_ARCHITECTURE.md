# Nikolai 0.3 — Technical Architecture

## 1. Hybrid Cognitive Architecture
Nikolai 0.3 utilizes a two-tier hybrid architecture designed for high-availability, low-latency edge coordination.

### 1.1 The Phi Silica Layer (Reflex Brain)
The **Silica Layer** is an asynchronous, event-driven engine written in Python (utilizing `asyncio`). It serves as the system's "reflexes," handling all non-blocking I/O and immediate reactions.

- **Event Bus:** A central `SilicaEventLoop` that routes events across the system without blocking.
- **Pipeline Watcher:** Asynchronously monitors the `modules/` directory for incoming GCLI artifacts.
- **Module Loader:** Handles the unpacking, validation, and registration of new modules (e.g., ShopperModule).
- **Node Coordinator:** Manages the registry and gRPC routing for external Shopper Assistant Nodes (SAN).
- **State Machine:** Fast, reflex-level state transitions (IDLE, SHOPPER_MODE, NAVIGATION_MODE).

### 1.2 The Async Executive Layer (Core Brain)
The **Executive Layer** sits above Silica and handles high-level reasoning, intent classification, and long-term planning.

- **AsyncCoreRuntime:** The central orchestrator that processes Silica events and issues strategic commands.
- **AsyncIntentEngine:** A non-blocking NLP engine that classifies user input into actionable intents.
- **AsyncContextManager:** Manages global state and persistent memory with async-safe locking.
- **AsyncTaskManager:** Schedules and monitors long-running reasoning tasks.

---

## 2. Communication and Data Flow

### 2.1 The Async Event Bridge
The two layers communicate via a bi-directional **Async Event Bridge**.
- **Downward (Reflex):** The Executive layer publishes strategic intents to Silica's event bus.
- **Upward (Telemetry):** Silica pushes telemetry, state updates, and module events up to the Executive layer's processing queue.

### 2.2 Input Handling (AsyncRespondLoop)
To ensure the system remains responsive, user input is handled by a non-blocking loop that utilizes a thread executor for `stdin` reads. This allows the system to continue processing SAN telemetry and background tasks while waiting for user input.

---

## 3. Integration with Shopper Assistant Node (SAN)
- **Networking:** Communication is routed over a secure **Tailscale/WireGuard** tunnel.
- **Protocol:** Telemetry is serialized using **Protobuf v3** for minimal battery and memory overhead on the mobile node.
- **Media:** Low-latency navigation mirroring is achieved via a **WebRTC** pipeline captured by Android's `MediaProjection` API.

---

## 4. Startup Sequence
1. **Reflex Init:** `SilicaEventLoop` and `SilicaPipelineWatcher` start monitoring.
2. **Executive Init:** `AsyncCoreRuntime` loads the project spine and initializes the context.
3. **Bridge Handshake:** The Python Bridge and Silica Bridge are wired together.
4. **Node Discovery:** Silica SAN Bridge opens the gRPC port on the Tailnet IP.
5. **Ready State:** The system prompts the user via the `AsyncRespondLoop`.
