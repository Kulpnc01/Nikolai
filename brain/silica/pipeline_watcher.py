import asyncio
from pathlib import Path
import logging
from typing import Set

logger = logging.getLogger(__name__)

class SilicaPipelineWatcher:
    def __init__(self, event_loop, modules_dir: Path):
        self.event_loop = event_loop
        self.modules_dir = modules_dir
        self.expected_artifacts = {
            "san_build_spec.txt",
            "san_final_spec.txt",
            "shopper_assistant_node_san.zip",
            "module_contract.json",
        }
        self.known_modules: Set[str] = set()

    async def watch_loop(self, poll_interval: float = 2.0):
        logger.info(f"Silica Pipeline Watcher monitoring: {self.modules_dir}")
        while True:
            if self.modules_dir.exists():
                for module_path in self.modules_dir.iterdir():
                    if module_path.is_dir() and module_path.name not in self.known_modules:
                        incoming = module_path / "pipeline" / "incoming"
                        if incoming.exists():
                            present = {p.name for p in incoming.iterdir() if p.is_file()}
                            if self.expected_artifacts.issubset(present):
                                logger.info(f"Artifacts detected for module: {module_path.name}")
                                self.known_modules.add(module_path.name)
                                await self.event_loop.publish("module_artifacts_ready", {
                                    "module_name": module_path.name, 
                                    "path": module_path
                                })
            await asyncio.sleep(poll_interval)
