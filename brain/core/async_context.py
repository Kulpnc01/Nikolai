import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class AsyncContextManager:
    """
    Refined AsyncContextManager with namespacing for multi-module isolation.
    Handles global state and non-blocking interactions with persistent memory.
    """
    def __init__(self, root_dir: Path, memory_dir: Path, modules_dir: Path):
        self.root_dir = root_dir
        self.memory_dir = memory_dir
        self.modules_dir = modules_dir
        self.state: Dict[str, Any] = {"global": {}, "modules": {}}
        self._lock = asyncio.Lock()

    async def update(self, key: str, value: Any, namespace: str = "global"):
        """Asynchronously update a state value with namespace protection."""
        async with self._lock:
            if namespace == "global":
                self.state["global"][key] = value
            else:
                if namespace not in self.state["modules"]:
                    self.state["modules"][namespace] = {}
                self.state["modules"][namespace][key] = value

    async def get(self, key: str, default: Any = None, namespace: str = "global") -> Any:
        """Asynchronously retrieve a state value from a specific namespace."""
        async with self._lock:
            target = self.state["global"] if namespace == "global" else self.state["modules"].get(namespace, {})
            return target.get(key, default)

    async def delete(self, key: str, namespace: str = "global"):
        """Asynchronously delete a state value."""
        async with self._lock:
            target = self.state["global"] if namespace == "global" else self.state["modules"].get(namespace, {})
            if key in target:
                del target[key]

    async def get_full_snapshot(self) -> Dict[str, Any]:
        """Returns a deep copy of the current state for reasoning."""
        import copy
        async with self._lock:
            # Simple flattening for diagnostic reasoning
            flat = self.state["global"].copy()
            for mod_ns, mod_data in self.state["modules"].items():
                flat[f"module_{mod_ns}"] = mod_data
            return copy.deepcopy(flat)

    async def load_memory(self, filename: str) -> Optional[str]:
        """Non-blocking read from the memory directory."""
        mem_file = self.memory_dir / filename
        if not mem_file.exists():
            return None
        try:
            return await asyncio.to_thread(mem_file.read_text, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read memory {filename}: {e}")
            return None

    async def save_memory(self, filename: str, content: str):
        """Non-blocking write to the memory directory."""
        mem_file = self.memory_dir / filename
        try:
            await asyncio.to_thread(mem_file.write_text, content, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to write memory {filename}: {e}")
