# Project Nikolai: Technical Architecture & Agent Interop

This document maps out the interaction between Nikolai's core modules and the external AI assistants (Gemini CLI & Copilot).

## 1. System Architecture (Hub-and-Spoke)

- **Central Hub**: `memory_mcp_server.py` (FastMCP) manages the SQLite database (`nikolai_memory.db`).
- **Spokes**:
  - **`agent_loop.py`**: The main execution engine. Polls for tasks, vision events, and triggers reminders.
  - **`vision_ingestion.py`**: Monitors RTSP camera streams for motion and logs to the Hub.
  - **`voice_interface.py`**: Provides STT (Whisper/local) and TTS (local) for the user.
  - **`control_center.py`**: Admin GUI for managing resources and network nodes.

## 2. Interaction Flow for Assistants

### **A. Reading System State**

1. **Grep/Read Files**: Gemini CLI/Copilot read the source code to understand logic.
2. **MCP Tooling**: Gemini CLI calls `read_memory()` or `get_tasks()` via the MCP server to understand the current context of the user's life and Nikolai's work.

### **B. Modifying System State**

1. **Strategic Changes**: Gemini CLI performs surgical file modifications to the "Spokes" (e.g., adding a new detection logic to `agent_loop.py`).
2. **Tactical Assistance**: Copilot provides inline suggestions for repetitive boilerplate or documentation within the Spokes.
3. **Memory Writes**: Both assistants MUST use `write_memory()` or `create_task()` when proposing a new persistent thought or action.

## 3. Communication Protocols

- **Log-First Principle**: Every major action taken by an assistant must be logged as an `event` with `source='gemini_cli'` or `source='copilot'`.
- **Hybrid Memory Sync**:
  - When an assistant creates a temporary scratchpad file, it must be named `scratch_[purpose].md`.
  - Once the work is done, the assistant must summarize the outcome in a call to `write_memory()`.

## 4. User-Interaction Priority

- **Voice Interface**: Nikolai's "Conversational/Active" mode uses `voice_interface.py` to bridge the gap between digital thoughts and the user's focus.
- **Conflict Handling**: If the user provides a voice command that contradicts a task in the database, the voice command triggers an immediate "Memory Update" that overrides the previous state.
