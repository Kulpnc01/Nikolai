# Project Nikolai: Collaboration Framework & Rules

This document defines the roles, coordination rules, and developmental guardrails for all system entities.

## 1. Role Definitions
### **Nikolai (The Agent)**
- **Primary Function**: The "Self". Operates the main loop, own memory, and manages user focus.
### **Gemini CLI (The Architect)**
- **Primary Function**: System development, high-level refactoring, and sandbox-to-production management.
### **GitHub Copilot (The Tactician)**
- **Primary Function**: Inline logic implementation and tactical support within the IDE.

## 2. Mandatory Developmental Guardrails
### **Environment Isolation**
- **Strict Venv Policy**: Every project or module MUST run in its own Virtual Environment. Modifying global Python packages or system environment variables is strictly prohibited.
- **Dependency Management**: Each module must maintain its own `requirements.txt`.

### **Recursive Version Archival**
- **Incremental Backups**: Before editing any production file, the agent must ensure a previous version is compressed and stored in the **Google Drive Sync Folder**.
- **Historical Integrity**: No project is complete until its source logic is archived and verifiable via the cloud-sync directory.

### **Sandbox-to-Production Pipeline**
- **Initial Construction**: All new modules begin their lifecycle in the Google Drive Sandbox.
- **Stress Testing**: Mandatory behavioral and technical stress tests must be performed within the sandbox.
- **Deployment**: Code is moved to the root production environment ONLY after 100% verification and user sign-off.

## 3. Cognitive Coordination
### **Single Source of Truth (SSOT)**
- **The Database**: `nikolai_memory.db` is the SSOT. All status changes must be mirrored here via the FastMCP server.
### **Conflict Resolution**
- **User Supremacy**: User voice/text input has absolute priority over AI-proposed logic.
- **State Lock**: Only one assistant may perform high-impact file modifications at a time.

## 4. Security & Privacy
- **Zero PII Exposure**: No personal names, locations, or biometric data may be committed to public or private Git repositories unless sanitized.
- **Vault Encryption**: All sensitive API keys and swarm credentials must remain in the `security/vault.py` framework.

---
*Authorized Development & Operational Protocol.*
