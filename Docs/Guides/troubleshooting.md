# Nikolai 0.3 Troubleshooting Guide

## 1. Connection Issues
### "SAN Node Offline"
- **Cause:** Tailscale is not running or the node ID is incorrect.
- **Fix:** Verify Tailscale status (`tailscale status`). Ensure the node is authorized on your tailnet.

## 2. Module Loading Failures
### "Module Not Activated"
- **Cause:** Missing `module_contract.json` or incorrect ZIP artifact naming.
- **Fix:** Check `modules/<ModuleName>/pipeline/incoming/`. Ensure the source artifact matches the naming convention (e.g., `shopper_assistant_node_san.zip`).

## 3. Runtime Exceptions
### "RuntimeError: Event loop is already running"
- **Cause:** Attempting to start multiple event loops in the same thread.
- **Fix:** Ensure `nikolai.py` is using the unified `asyncio.run()` entry point and all background tasks are scheduled via `asyncio.create_task()`.

## 4. Diagnostic Help
Use the built-in diagnostic engine for real-time analysis:
`> help diagnose system`
This will parse current telemetry and identify bottlenecks or errors in the reflex layer.
