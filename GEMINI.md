# Project Nikolai: Core Mandates

## Objective

Nikolai is an all-encompassing life assistant designed to combat ADHD, distractions, and forgetfulness. He enhances the user's natural processes, prioritizes goals, and manages a revenue stream to support the user's personal business.

## Technical Standards

- **Memory First**: All long-term state, tasks, and significant events MUST be stored in the central SQLite database (`nikolai_memory.db`) via the MCP server.
- **Hybrid Sync Strategy**: Assistants (Gemini CLI, Copilot, Nikolai) may use local files or scratchpads for tactical work but MUST synchronize the final state back to the MCP database to ensure consistency.
- **Local-First, Cloud-Supplemented**: Operations should prioritize local hardware (vision, voice, database). Cloud resources (Google Pro, Azure, Copilot) are utilized for high-compute or specialized tasks.
- **Surgical Updates**: Code modifications must be precise and follow established patterns in `memory_mcp_server.py`, `agent_loop.py`, and `vault.py`.

## ADHD & Productivity Guardrails

- **User-Centric Authority**: The user is the final arbiter of task priority and scheduling. Nikolai suggests; the user decides.
- **Multi-Channel Reminders**: Reminders must be delivered via **Voice** (`voice_interface.py`), **Desktop Toast** (PowerShell/win32), and logged to `REMINDERS.txt`.
- **Behavioral Detection**:
  - **Hyperfocus Watcher**: Flag and remind the user if a single task (priority 1 or 2) exceeds 40 minutes without a status update.
  - **Priority Drift Guard**: Flag if the user initiates a new task while a higher-priority task is still in 'pending' status.
- **Granular Decomposition**: Large goals must be broken into small, atomic tasks logged in the memory bank to prevent overwhelm.

## Security & Business

- **Vault Integrity**: All credentials and sensitive data MUST stay encrypted within the `vault.py` framework. Never log or print raw secrets.
- **Revenue Scope**: Nikolai manages and operates digital content creation pipelines, AI solution delivery for low-tech companies, and affiliate marketing automation.
- **Shared Responsibility**: All project entities (Gemini, Copilot, Nikolai) are responsible for both the development and operation of revenue-generating tools.
- **Audit Log**: Every automated action taken by Nikolai or the assistants must be logged in the `event_log` for transparency.