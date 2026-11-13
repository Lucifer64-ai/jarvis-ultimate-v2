"""
JARVIS - File Saver Service
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class FileSaver:
    """Service for saving files to disk."""

    def __init__(self, base_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(base_dir or os.getenv("JARVIS_OUTPUT_DIR", "jarvis_output"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"FileSaver initialized. Output dir: {self.base_dir.absolute()}")

    def save_files(self, files: Dict[str, str], project_name: Optional[str] = None, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Save files to disk."""
        if not files:
            return {"status": "error", "message": "No files to save"}

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if project_name:
                safe_name = "".join(c for c in project_name if c.isalnum() or c in (" ", "-", "_")).strip()
                safe_name = safe_name.replace(" ", "_")[:50]
                project_dir = self.base_dir / f"{safe_name}_{timestamp}"
            else:
                project_dir = self.base_dir / f"project_{timestamp}"

            project_dir.mkdir(parents=True, exist_ok=True)

            saved_files = []
            for filename, content in files.items():
                file_path = project_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)

                mode = "wb" if isinstance(content, bytes) else "w"
                encoding = None if mode == "wb" else "utf-8"

                with open(file_path, mode, encoding=encoding) as f:
                    f.write(content)

                saved_files.append({
                    "filename": filename,
                    "path": str(file_path.absolute()),
                    "size": len(content) if isinstance(content, (str, bytes)) else 0
                })

                self.logger.info(f"Saved: {file_path}")

            return {
                "status": "success",
                "project_dir": str(project_dir.absolute()),
                "files_saved": len(saved_files),
                "files": saved_files
            }
        except Exception as e:
            self.logger.error(f"Error saving files: {e}")
            return {"status": "error", "message": f"Save error: {str(e)}"}

    def list_projects(self) -> List[Dict[str, Any]]:
        projects = []
        if not self.base_dir.exists():
            return projects

        for item in self.base_dir.iterdir():
            if item.is_dir():
                files = [f for f in item.glob("**/*") if f.is_file()]
                projects.append({
                    "name": item.name,
                    "path": str(item.absolute()),
                    "files_count": len(files),
                    "created": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })

        return sorted(projects, key=lambda x: x["created"], reverse=True)


_file_saver_instance = None

def get_file_saver() -> FileSaver:
    global _file_saver_instance
    if _file_saver_instance is None:
        _file_saver_instance = FileSaver()
    return _file_saver_instance
