# Project Nikolai: Collaboration Framework

This document defines the roles and coordination rules for Gemini CLI, GitHub Copilot, and Project Nikolai (the agent system).

## 1. Role Definitions

### **Nikolai (The Agent)**

- **Primary Function**: The "Self". Operates the main `agent_loop.py`, executes long-running tasks, monitors vision/voice events, and provides user reminders.
- **Responsibility**: Owning the memory database and ensuring the user stays on target.

### **Gemini CLI (The Architect)**

- **Primary Function**: System development, complex refactoring, and high-level logic implementation.
- **Responsibility**: Expanding Nikolai's "body" and "brain", ensuring technical integrity, and providing deep codebase analysis.

### **GitHub Copilot (The Tactician)**

- **Primary Function**: Inline code-completion, rapid documentation, and local logic implementation.
- **Responsibility**: Streamlining the user's manual coding experience and providing tactical support within the IDE.

## 2. Coordination Rules

### **Single Source of Truth (SSOT)**

- **The Database**: `nikolai_memory.db` is the SSOT. Any change in task state or memory must be synchronized here via `memory_mcp_server.py`.
- **Hybrid Workflow**: When Gemini or the user is working on a feature, a "scratchpad" file (e.g., `scratch_new_feature.md`) can be used. Final decisions and results MUST be logged as a "memory" or "task" in the MCP server.

### **Conflict Resolution**

- **User Supremacy**: If Gemini CLI and Nikolai's loop propose conflicting priorities, the user's explicit input (voice or text) has absolute priority.
- **State Lock**: Only one assistant should perform high-impact file modifications at a time. Coordination occurs by checking the `event_log` for recent "development" events.

### **ADHD & Focus Protocol**

- **Notification Hook**: The `agent_loop.py` emits "Focus Reminders" via Voice, PowerShell Toast, and `REMINDERS.txt`.
- **Hyperfocus Alert**: If a Priority 1 or 2 task hasn't been updated for **40 minutes**, Nikolai must trigger a reminder.
- **Priority Drift Alert**: If a new task is started before higher-priority tasks are cleared, Nikolai will log a warning and notify the user.
- **Small Batches**: All directives from the user must be broken down by Gemini CLI into discrete, actionable steps recorded in the `tasks` table.

## 3. Revenue Stream & Security

- **Strict Vault Policy**: No entity (Nikolai, Gemini, Copilot) is permitted to expose credentials outside of `vault.py`.
- **Audit Requirement**: Any financial operation (e.g., API call to a trading platform, subscription check) must log its intent *before* execution and its result *after* execution to the `event_log`.
