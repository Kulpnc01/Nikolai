# Project Nikolai: Cognitive Agent & Memory Hub

Nikolai is a modular AI agent system designed to act as a "Digital Self." It integrates persistent long-term memory, real-time vision ingestion, and a local voice interface into a unified cognitive loop.

## 核心 (Core Architecture)

*   **Intelligence Core (`/core`)**: Manages the main cognitive loop, task prioritization, and hyperfocus protocols.
*   **Memory Hub (`/memory`)**: A FastMCP-powered SQLite database that serves as the Single Source of Truth (SSOT) for all agent thoughts and events.
*   **Sense Interfaces (`/interface`)**: Handles RTSP vision streams and local STT/TTS (Whisper) communication.
*   **Security Vault (`/security`)**: Provides Fernet-encrypted storage for sensitive credentials and network nodes.

## System Capabilities

- **Autonomous Loop**: Continuously monitors tasks and environmental events to keep the user on target.
- **Multimodal Ingestion**: Weaves together vision events, voice commands, and manual memory writes.
- **Swarm Management**: Integrated GUI for managing network resources, cameras, and encrypted credentials.
- **ADHD/Focus Protocols**: Built-in logic for hyperfocus alerts and priority drift notifications.

## Quick Start

1.  **Initialize Memory**:
    ```bash
    python memory/Initialize-memory.py
    ```
2.  **Start the Loop**:
    ```bash
    python core/agent_loop.py
    ```
3.  **Launch Control Center**:
    ```bash
    python core/control_center.py
    ```

## AI Orchestration
Nikolai is designed to be managed and expanded by AI architects. Refer to `RULES.md` and `TECHNICAL_ARCHITECTURE.md` for the collaboration framework.

---
*Authorized Forensic & Digital Twin Research Protocol.*
