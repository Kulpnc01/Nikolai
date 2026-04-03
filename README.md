# Project Nikolai: Cognitive Agent & Memory Hub

Nikolai is a modular AI agent system designed to act as a "Digital Self." It integrates persistent long-term memory, real-time vision ingestion, and a local voice interface into a unified cognitive loop.

## 核心 (Core Architecture)

*   **Intelligence Core (`/core`)**: Manages the main cognitive loop, task prioritization, and hyperfocus protocols.
*   **Memory Hub (`/memory`)**: A FastMCP-powered SQLite database that serves as the Single Source of Truth (SSOT).
*   **Sense Interfaces (`/interface`)**: Handles RTSP vision streams and local STT/TTS communication.
*   **Security Vault (`/security`)**: Provides Fernet-encrypted storage for sensitive credentials.

## Mandatory Development Protocols

### 1. Environment Isolation
Every new module or major project MUST receive its own independent Virtual Environment (`venv`). Modifying global system variables or global Python packages is strictly prohibited.

### 2. Sandbox-to-Production Pipeline
All developmental work occurs within a dedicated **Google Drive-synced Sandbox**.
- Code is stress-tested and verified at 100% in the sandbox before migration to root production.
- Incremental backups (compressed archives) of all production files are stored in the Drive folder before modification.

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
Nikolai is governed by the `GEMINI.md` mandates and `RULES.md` collaboration framework. Refer to these files for detailed developmental guardrails.

---
*Authorized Forensic & Digital Twin Research Protocol.*
