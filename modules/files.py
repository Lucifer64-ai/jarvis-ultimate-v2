"""
Модуль работы с файлами JARVIS
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

try:
    from send2trash import send2trash
except ImportError:
    send2trash = None


class FileModule:
    """Модуль работы с файлами и папками."""

    def __init__(self, brain):
        self.brain = brain

    def list_directory(self, path: str = ".") -> List[Dict]:
        """Список файлов в директории."""
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
        """Создать файл."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"status": "ok", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_file(self, path: str) -> Dict:
        """Удалить файл в корзину."""
        if send2trash is None:
            # Fallback: use os.unlink (permanent delete)
            try:
                os.unlink(path)
                return {"status": "ok", "message": f"Файл '{path}' удалён"}
            except Exception as e:
                return {"status": "error", "message": f"send2trash недоступен: {e}"}
        try:
            send2trash(path)
            return {"status": "ok", "message": f"Файл '{path}' перемещён в корзину"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def copy_file(self, src: str, dst: str) -> Dict:
        """Копировать файл."""
        try:
            shutil.copy2(src, dst)
            return {"status": "ok", "src": src, "dst": dst}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def move_file(self, src: str, dst: str) -> Dict:
        """Переместить файл."""
        try:
            shutil.move(src, dst)
            return {"status": "ok", "src": src, "dst": dst}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_directory(self, path: str) -> Dict:
        """Создать директорию."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return {"status": "ok", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
