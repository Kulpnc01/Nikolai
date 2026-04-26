import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DiagnosticEngine:
    """
    The intelligence behind HelpDiagnosticModule.
    Integrates with Silica and the Async Executive Layer.
    """
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.docs_dir = root_dir / "Docs"
        self.logs_dir = root_dir / "nervous_system"

    async def handle_help_request(self, query: str, context: Dict[str, Any]) -> str:
        """
        Main entry point for help queries.
        """
        q = query.lower()
        
        # 1. Check for Architectural Queries
        if any(k in q for k in ["architecture", "silica", "reflex", "how does it work"]):
            return await self._get_architectural_help()

        # 2. Check for Operational Queries (SAN/Shopper)
        if any(k in q for k in ["shopper", "san", "shipt", "node"]):
            return await self._get_san_help(context)

        # 3. Check for Diagnostic/Error Queries
        if any(k in q for k in ["error", "problem", "issue", "diagnose"]):
            return await self._diagnose_system(context)

        # Fallback: List available knowledge areas
        return (
            "I can help with the following areas:\n"
            "- **Architecture:** Explain Phi Silica and the Executive layers.\n"
            "- **SAN Operations:** Help with Shopper Module and Android nodes.\n"
            "- **System Diagnostics:** Analyze logs and current runtime state.\n"
            "What would you like to explore?"
        )

    async def _get_architectural_help(self) -> str:
        arch_file = self.docs_dir / "Architecture" / "TECHNICAL_ARCHITECTURE.md"
        if arch_file.exists():
            content = await asyncio.to_thread(arch_file.read_text, encoding="utf-8")
            # Extract summary
            return f"### Nikolai 0.3 Architecture\n{content[:500]}...\n\n(See {arch_file} for full details)"
        return "Technical architecture documentation is currently missing."

    async def _get_san_help(self, context: dict) -> str:
        san_spec = self.root_dir / ".gemini" / "ShopperModule" / "Specifications" / "SAN_Technical_Specification.md"
        state = context.get("silica_state", "IDLE")
        
        response = f"### SAN Status: {state}\n"
        if san_spec.exists():
            response += "The SAN (Shopper Assistant Node) is a low-latency Android bridge to Nikolai.\n"
            response += f"Reference: {san_spec}"
        else:
            response += "Shopper Assistant Node specifications are not currently loaded."
        return response

    async def _diagnose_system(self, context: dict) -> str:
        active_modules = context.get("active_modules", [])
        last_event = context.get("last_silica_event", {})
        
        report = "### System Diagnostic Report\n"
        report += f"- **Active Modules:** {', '.join(active_modules) if active_modules else 'None'}\n"
        report += f"- **Reflex State:** {context.get('silica_state', 'IDLE')}\n"
        
        if not active_modules:
            report += "- **Alert:** No modules are currently active. Use 'prepare shopper module' to begin.\n"
        
        if last_event.get("error"):
            report += f"- **Recent Error:** {last_event['error']}\n"
            
        return report
