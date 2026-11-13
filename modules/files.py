"""
£¿°в»µ½иµ °¹»°¼и JARVIS
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List
from send2trash import send2trash


class FileModule:
    """£¿°в»µ½иµ °¹»¾в¾¹ иµ¼¾¹."""

    def __init__(self, brain):
        self.brain = brain

    def list_directory(self, path: str = ".") -> List[Dict]:
        """¡¿и¾º °¹»¾в в ´иµº¾ии."""
        try:
            items = []
            for item in Path(path).iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0
                })
            return items
        except Exception as e:
            return [{"error": str(e)}]

    def create_file(self, path: str, content: str = "") -> Dict:
        """¡¾·´° °¹»."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"status": "ok", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_file(self, path: str) -> Dict:
        """£´°»и °¹» в º¾·и½."""
        try:
            send2trash(path)
            return {"status": "ok", "message": f"¤°¹» '{path}' ¿µµ¼µ½ в º¾·и½"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def copy_file(self, src: str, dst: str) -> Dict:
        """¾¿и¾в° °¹»."""
        try:
            shutil.copy2(src, dst)
            return {"status": "ok", "src": src, "dst": dst}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def move_file(self, src: str, dst: str) -> Dict:
        """µµ¼µи °¹»."""
        try:
            shutil.move(src, dst)
            return {"status": "ok", "src": src, "dst": dst}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_directory(self, path: str) -> Dict:
        """¡¾·´° ´иµº¾и."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return {"status": "ok", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
