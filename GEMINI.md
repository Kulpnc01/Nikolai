# Project Nikolai: Core Mandates

## Objective
Nikolai is an all-encompassing life assistant designed to combat ADHD, distractions, and forgetfulness. He enhances the user's natural processes, prioritizes goals, and manages a revenue stream to support the user's personal business.

## Development Sandboxing & Isolation (STRICT MANDATE)
To protect system stability and maintain environment integrity, all developmental work must follow these protocols:
- **Per-Module Isolation**: EVERY new project, module, or major feature branch MUST receive its own independent Virtual Environment (`venv`). 
- **System Variable Protection**: Assistants are strictly forbidden from modifying global system environment variables during development. All environment-specific variables must be scoped to the local `.env` or the module's `venv`.
- **Sandbox-to-Production Pipeline**: All new code will be developed and stress-tested in a dedicated sandbox directory. Transition to the root production environment is permitted ONLY after 100% successful verification and user approval.

## Recursive Archival & Backup
- **Version Persistence**: Before any significant file modification, a compressed archive (`.zip`) of the PREVIOUS version of the file or directory must be generated.
- **Google Drive Synchronization**: All backups and the primary development environment must be located in a directory synchronized with Google Drive. This directory acts as the root for all new developmental logic.
- **Fail-Safe Recovery**: In the event of logic corruption or system drift, Nikolai must be able to restore the system state from the latest Google Drive-synced archive.

## Technical Standards
- **Memory First**: All long-term state, tasks, and significant events MUST be stored in the central SQLite database (`nikolai_memory.db`) via the MCP server.
- **Hybrid Sync Strategy**: Assistants may use scratchpads for tactical work but MUST synchronize final state to the MCP database.
- **Local-First, Cloud-Supplemented**: Prioritize local hardware (NPU/GPU) for inference. Use Cloud (Azure/Google Pro) only for high-compute or specialized tasks.

## ADHD & Productivity Guardrails
- **Hyperfocus Watcher**: Flag and remind the user if a priority 1 or 2 task exceeds 40 minutes without an update.
- **Priority Drift Guard**: Flag if the user initiates a new task while a higher-priority task remains 'pending'.
- **Granular Decomposition**: Break large goals into atomic, actionable steps in the memory bank.

## Security & Business
- **Vault Integrity**: Credentials must remain encrypted within the `vault.py` framework.
- **Shared Responsibility**: All project entities (Gemini, Copilot, Nikolai) are responsible for both development and operation of revenue-generating tools.
- **Audit Log**: Every automated action must be logged in the `event_log` for transparency.
