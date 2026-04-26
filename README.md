# Nikolai 0.3 — Hybrid Asynchronous Cognitive Engine

Nikolai 0.3 is a high-performance, edge-coordinated cognitive engine designed for low-latency logistical assistance and autonomous UI interaction.

## 🚀 Key Features
- **Hybrid Cognitive Architecture:** Separation of high-level reasoning (Executive Layer) and fast-reflex I/O (Phi Silica Layer).
- **Asynchronous Core:** Built on `asyncio` for non-blocking telemetry ingestion and command dispatch.
- **Edge Node Coordination:** Native support for Android-based Shopper Assistant Nodes (SAN) via secure gRPC.
- **Secure Mesh Networking:** All communication is routed over an encrypted Tailscale/WireGuard tunnel.
- **Contract-Driven Modules:** Dynamic module loading and validation system.

## 📂 Project Structure
- `brain/core/`: Executive Reasoning & Orchestration.
- `brain/silica/`: Reflex Layer & gRPC Communication.
- `modules/`: Autonomous agent modules (Shopper, Help/Diagnostic).
- `Docs/`: Comprehensive technical architecture and guides.
- `build_scripts/`: Sequenced (00-07) "Self-Healing" build pipeline.

## 🛠️ Installation & Usage

### 1. Prerequisites
- Python 3.12+ (Python 3.14 recommended)
- PowerShell Core (pwsh)
- Tailscale (for edge node connectivity)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Nikolai
```powershell
# From the project root
./nikolai.ps1
```

## 📘 Documentation
Detailed documentation is available in the `Docs/` directory:
- [Technical Architecture](./Docs/Architecture/TECHNICAL_ARCHITECTURE.md)
- [Getting Started Guide](./Docs/Guides/getting-started.md)
- [Troubleshooting](./Docs/Guides/troubleshooting.md)

## ⚖️ Governance
Nikolai 0.3 is governed by the principles of architectural locking and zero-drift development defined in the `project_spine.json`.

---
**Version:** 0.3 (Hardened Async)
**Author:** Kulpnc01
