"""
£¿°²»µ½¸µ °¹»°¼¸ JARVIS
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List
from send2trash import send2trash


class FileModule:
    """£¿°²»µ½¸µ °¹»¾²¾¹ ¸µ¼¾¹."""

    def __init__(self, brain):
        self.brain = brain

    def list_directory(self, path: str = ".") -> List[Dict]:
        """¡¿¸¾º °¹»¾² ² ´¸µº¾¸¸."""
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
        """£´°»¸ °¹» ² º¾·¸½."""
        try:
            send2trash(path)
            return {"status": "ok", "message": f"¤°¹» '{path}' ¿µµ¼µ½ ² º¾·¸½"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def copy_file(self, src: str, dst: str) -> Dict:
        """¾¿¸¾²° °¹»."""
        try:
            shutil.copy2(src, dst)
            return {"status": "ok", "src": src, "dst": dst}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def move_file(self, src: str, dst: str) -> Dict:
        """µµ¼µ¸ °¹»."""
        try:
            shutil.move(src, dst)
            return {"status": "ok", "src": src, "dst": dst}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_directory(self, path: str) -> Dict:
        """¡¾·´° ´¸µº¾¸."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return {"status": "ok", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
