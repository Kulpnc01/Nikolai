import asyncio
import json
import zipfile
from pathlib import Path
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SilicaModuleLoader:
    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.loaded_modules: Dict[str, Any] = {}
        self.event_loop.subscribe("module_artifacts_ready", self.handle_artifacts_ready)

    async def handle_artifacts_ready(self, payload: dict):
        module_name = payload["module_name"]
        module_path: Path = payload["path"]
        logger.info(f"Silica Module Loader verifying: {module_name}")
        
        success = await asyncio.to_thread(self._unpack_and_validate, module_path)
        
        if success:
            contract_path = module_path / "pipeline" / "incoming" / "module_contract.json"
            try:
                with open(contract_path, "r") as f:
                    contract = json.load(f)
                
                self.loaded_modules[module_name] = {
                    "path": str(module_path),
                    "contract": contract,
                    "status": "active"
                }
                logger.info(f"Module {module_name} activated successfully.")
                await self.event_loop.publish("module_loaded", {
                    "module_name": module_name, 
                    "contract": contract
                })
            except Exception as e:
                logger.error(f"Contract parsing failed for {module_name}: {e}")
                await self.event_loop.publish("module_error", {"module": module_name, "error": str(e)})

    def _unpack_and_validate(self, module_path: Path) -> bool:
        incoming = module_path / "pipeline" / "incoming"
        zip_path = incoming / "shopper_assistant_node_san.zip"
        extract_dir = module_path / "android_app"
        
        try:
            if zip_path.exists() and zipfile.is_zipfile(zip_path):
                extract_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                return True
        except Exception as e:
            logger.error(f"Failed to unpack {zip_path}: {e}")
        return False
