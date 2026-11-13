"""
¡¸µ¼° °»¸°¾² JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class AliasSystem:
    """£¿°²»µ½¸µ ¿¾»·¾²°µ»º¸¼¸ °»¸°°¼¸ для º¾¼°½´."""

    def __init__(self, brain):
        self.brain = brain
        self.aliases_file = Path("data/aliases.json")
        self.aliases_file.parent.mkdir(exist_ok=True)
        self.aliases: Dict[str, str] = self._load_aliases()

    def _load_aliases(self) -> Dict[str, str]:
        """°³·º° °»¸°¾² ¸· °¹»°."""
        if self.aliases_file.exists():
            with open(self.aliases_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_aliases(self):
        """¡¾°½µ½¸µ °»¸°¾²."""
        with open(self.aliases_file, 'w', encoding='utf-8') as f:
            json.dump(self.aliases, f, ensure_ascii=False, indent=2)

    def add_alias(self, alias: str, command: str) -> Dict:
        """¾±°²»µ½¸µ ½¾²¾³¾ °»¸°°."""
        alias_lower = alias.lower().strip()
        command_lower = command.lower().strip()
        
        self.aliases[alias_lower] = command_lower
        self._save_aliases()
        
        self.brain.logger.info(f"¾±°²»µ½ °»¸°: '{alias}'  '{command}'")
        return {
            "status": "ok",
            "alias": alias_lower,
            "command": command_lower,
            "message": f"»¸° '{alias}' ¾°½µ½"
        }

    def remove_alias(self, alias: str) -> Dict:
        """£´°»µ½¸µ °»¸°°."""
        alias_lower = alias.lower().strip()
        
        if alias_lower in self.aliases:
            del self.aliases[alias_lower]
            self._save_aliases()
            return {"status": "ok", "message": f"»¸° '{alias}' ´°»µ½"}
        
        return {"status": "error", "message": "»¸° ½µ ½°¹´µ½"}

    def resolve_alias(self, text: str) -> str:
        """ °·µµ½¸µ °»¸°° ² º¾¼°½´."""
        text_lower = text.lower().strip()
        
        # ¢¾½¾µ ¾²¿°´µ½¸µ
        if text_lower in self.aliases:
            return self.aliases[text_lower]
        
        # §°¸½¾µ ¾²¿°´µ½¸µ (°»¸° ² ½°°»µ º¾¼°½´)
        for alias, command in self.aliases.items():
            if text_lower.startswith(alias):
                # °¼µ½µ¼ °»¸° ½° º¾¼°½´
                return text_lower.replace(alias, command, 1)
        
        return text

    def list_aliases(self) -> List[Dict]:
        """¡¿¸¾º ²µ °»¸°¾²."""
        return [
            {"alias": alias, "command": command}
            for alias, command in self.aliases.items()
        ]

    def clear_aliases(self) -> Dict:
        """¸º° ²µ °»¸°¾²."""
        count = len(self.aliases)
        self.aliases = {}
        self._save_aliases()
        return {"status": "ok", "message": f"£´°»µ½¾ {count} °»¸°¾²"}

    def get_alias_stats(self) -> Dict:
        """¡°¸¸º° °»¸°¾²."""
        return {
            "total_aliases": len(self.aliases),
            "aliases": list(self.aliases.keys())
        }
