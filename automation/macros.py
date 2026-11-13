"""
¡¸µ¼° ¼°º¾¾² JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List


class MacroManager:
    """£¿°²»µ½¸µ ¼°º¾°¼¸."""

    def __init__(self, brain):
        self.brain = brain
        self.macros_dir = Path("macros")
        self.macros_dir.mkdir(exist_ok=True)
        self.macros: Dict[str, Dict] = {}
        self._load_macros()

    def _load_macros(self):
        """°³·º° ¼°º¾¾² ¸· °¹»¾²."""
        for file in self.macros_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.macros[file.stem] = data
            except Exception as e:
                self.brain.logger.error(f"¸±º° ·°³·º¸ ¼°º¾° {file}: {e}")

    def create_macro(self, name: str, commands: List[str]) -> Dict:
        """¡¾·´° ¼°º¾."""
        macro = {
            "name": name,
            "commands": commands,
            "created": str(datetime.now())
        }
        
        file_path = self.macros_dir / f"{name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(macro, f, ensure_ascii=False, indent=2)
        
        self.macros[name] = macro
        return {"status": "ok", "name": name}

    def execute_macro(self, name: str) -> Dict:
        """¿¾»½¸ ¼°º¾."""
        if name not in self.macros:
            return {"status": "error", "message": "°º¾ ½µ ½°¹´µ½"}
        
        macro = self.macros[name]
        results = []
        
        for command in macro["commands"]:
            result = self.brain.execute_command(command)
            results.append(result)
        
        return {"status": "ok", "results": results}

    def list_macros(self) -> List[str]:
        """¡¿¸¾º ¼°º¾¾²."""
        return list(self.macros.keys())

    def delete_macro(self, name: str) -> Dict:
        """£´°»¸ ¼°º¾."""
        if name in self.macros:
            file_path = self.macros_dir / f"{name}.json"
            if file_path.exists():
                file_path.unlink()
            del self.macros[name]
            return {"status": "ok"}
        return {"status": "error", "message": "°º¾ ½µ ½°¹´µ½"}
