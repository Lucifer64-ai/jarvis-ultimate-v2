"""
¡иµ¼° ¼°º¾¾в JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List


class MacroManager:
    """£¿°в»µ½иµ ¼°º¾°¼и."""

    def __init__(self, brain):
        self.brain = brain
        self.macros_dir = Path("macros")
        self.macros_dir.mkdir(exist_ok=True)
        self.macros: Dict[str, Dict] = {}
        self._load_macros()

    def _load_macros(self):
        """°³·º° ¼°º¾¾в и· °¹»¾в."""
        for file in self.macros_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.macros[file.stem] = data
            except Exception as e:
                self.brain.logger.error(f"агента ·°³·ºи ¼°º¾° {file}: {e}")

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
        """¿¾»½и ¼°º¾."""
        if name not in self.macros:
            return {"status": "error", "message": "°º¾ ни ½°¹´µ½"}
        
        macro = self.macros[name]
        results = []
        
        for command in macro["commands"]:
            result = self.brain.execute_command(command)
            results.append(result)
        
        return {"status": "ok", "results": results}

    def list_macros(self) -> List[str]:
        """¡¿и¾º ¼°º¾¾в."""
        return list(self.macros.keys())

    def delete_macro(self, name: str) -> Dict:
        """£´°»и ¼°º¾."""
        if name in self.macros:
            file_path = self.macros_dir / f"{name}.json"
            if file_path.exists():
                file_path.unlink()
            del self.macros[name]
            return {"status": "ok"}
        return {"status": "error", "message": "°º¾ ни ½°¹´µ½"}
