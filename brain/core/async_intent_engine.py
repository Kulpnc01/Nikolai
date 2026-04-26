import asyncio
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

@dataclass
class Intent:
    name: str
    raw_text: str
    entities: Dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0

class AsyncIntentEngine:
    """
    Refined Intent Engine with Regex-based Entity Extraction and pattern matching.
    """
    def __init__(self):
        # Patterns for extracting modules, nodes, and actions
        self.patterns = {
            "prepare_module": r"(?:prepare|init|setup)\s+(\w+)(?:\s+module)?",
            "node_command": r"(?:send|tell|dispatch)\s+(\w+)\s+to\s+node\s+(\w+)",
            "diagnose": r"(?:diagnose|check|repair)\s+(\w+)",
            "await_pipeline": r"(?:wait|await|listen|watch)\s+(?:for\s+)?(?:gcli\s+)?pipeline"
        }
        
        # Simple keyword fallback
        self.keywords = {
            "exit": ["exit", "quit", "shutdown"],
            "status": ["status", "health", "state", "system check"],
            "help": ["help", "commands", "what can you do", "explain"]
        }

    async def classify(self, text: str) -> Optional[Intent]:
        """
        Asynchronously process and classify the user input.
        """
        if not text:
            return None

        # Simulate NLP processing delay for future LLM integration readiness
        await asyncio.sleep(0.01) 
        
        t = text.strip().lower()
        entities = {}

        # 1. Pattern Matching with Entity Extraction
        for intent_name, pattern in self.patterns.items():
            match = re.search(pattern, t)
            if match:
                if intent_name == "prepare_module":
                    entities["module"] = match.group(1)
                elif intent_name == "node_command":
                    entities["action"] = match.group(1)
                    entities["node"] = match.group(2)
                elif intent_name == "diagnose":
                    entities["target"] = match.group(1)
                
                logger.debug(f"Intent classified (Pattern): {intent_name} with entities {entities}")
                return Intent(name=intent_name, raw_text=text, entities=entities)

        # 2. Check explicit keyword mappings
        for intent_name, phrases in self.keywords.items():
            if any(phrase in t for phrase in phrases):
                logger.debug(f"Intent classified (Keyword): {intent_name}")
                return Intent(name=intent_name, raw_text=text)

        # Fallback to generic free text
        logger.debug(f"Intent classified: free_text")
        return Intent(name="free_text", raw_text=text)
