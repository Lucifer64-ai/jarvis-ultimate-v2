"""
App Launcher - °¿º голосовые µµ· JARVIS
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging


class AppLauncher:
    """£¿°в»µ½иµ ·°¿º¾¼ голосовые."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.apps_file = Path("data/apps.json")
        self.apps_file.parent.mkdir(exist_ok=True)
        self.apps: Dict[str, str] = self._load_apps()

    def _load_apps(self) -> Dict[str, str]:
        """°³·º° ¿иº° голосовые."""
        if self.apps_file.exists():
            with open(self.apps_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # µ¾»½µ голосов
        return {
            "±»¾º½¾": "notepad.exe",
            "º°»º»¾": "calc.exe",
            "¿¾в¾´½иº": "explorer.exe",
            "±°·µ": "chrome.exe",
            "¾¼": "chrome.exe",
            "°¹¾º": "firefox.exe",
            "edge": "msedge.exe",
            "µ¼и½°»": "cmd.exe",
            "º¾¼°½´½° ¾º°": "cmd.exe",
            "powershell": "powershell.exe",
            "½°¾¹ºи": "ms-settings:",
            "´и¿µµ ·°´°": "taskmgr.exe",
            "paint": "mspaint.exe",
            "¾¾³°ии": "ms-photos:",
            "¼°³°·и½": "ms-windows-store:",
            "¿¾°": "outlookmail:",
            "º°»µ½´°": "outlookcal:",
            "youtube": "https://youtube.com",
            "±": "https://youtube.com",
            "³³»": "https://google.com",
            "github": "https://github.com",
            "µ»µ³°¼": "telegram.exe",
            "discord": "discord.exe",
            "¿¾и°¹": "spotify.exe",
            "vlc": "vlc.exe",
        }

    def _save_apps(self):
        """¡¾°ни½иµ ¿иº° голосовые."""
        with open(self.apps_file, 'w', encoding='utf-8') as f:
            json.dump(self.apps, f, ensure_ascii=False, indent=2)

    def launch(self, app_name: str) -> Dict:
        """°¿º голосов."""
        app_name_lower = app_name.lower().strip()
        
        # ¾иº в ¿иºµ
        if app_name_lower in self.apps:
            app_path = self.apps[app_name_lower]
            
            try:
                # »и ¾ URL
                if app_path.startswith("http://") or app_path.startswith("https://"):
                    subprocess.Popen(["start", app_path], shell=True)
                    return {"status": "ok", "message": f"ºв° {app_name}..."}
                
                # »и ¾ º¾¼°½´° Windows
                elif app_path.startswith("ms-"):
                    subprocess.Popen(["start", app_path], shell=True)
                    return {"status": "ok", "message": f"ºв° {app_name}..."}
                
                # »и ¾ exe °¹»
                else:
                    subprocess.Popen(app_path, shell=True)
                    return {"status": "ok", "message": f"°¿º° {app_name}..."}
            
            except Exception as e:
                self.logger.error(f"агента ·°¿º° {app_name}: {e}")
                return {"status": "error", "message": f"µ ´°»¾ ·°¿и {app_name}: {e}"}
        
        return {"status": "error", "message": f"и»¾¶µ½иµ '{app_name}' ни ½°¹´µ½¾. ¡º°¶иµ '´¾±°в голосовµ {app_name}'"}

    def add_app(self, name: str, path: str) -> Dict:
        """¾±°ви ½¾в¾µ голосовµ."""
        name_lower = name.lower().strip()
        self.apps[name_lower] = path
        self._save_apps()
        
        self.logger.info(f"¾±°в»µ½¾ голосовµ: {name} ¢ {path}")
        return {"status": "ok", "message": f"и»¾¶µ½иµ '{name}' ´¾±°в»µ½¾"}

    def remove_app(self, name: str) -> Dict:
        """£´°»и голосовµ."""
        name_lower = name.lower().strip()
        
        if name_lower in self.apps:
            del self.apps[name_lower]
            self._save_apps()
            return {"status": "ok", "message": f"и»¾¶µ½иµ '{name}' ´°»µ½¾"}
        
        return {"status": "error", "message": f"и»¾¶µ½иµ '{name}' ни ½°¹´µ½¾"}

    def list_apps(self) -> Dict:
        """¡¿и¾º вµ голосовые."""
        apps_list = [f"¢¢ {name}" for name in sorted(self.apps.keys())]
        return {
            "status": "ok",
            "message": f"¾¿½¾ {len(self.apps)} голосовые:\n" + "\n".join(apps_list[:20]) + ("\n..." if len(apps_list) > 20 else "")
        }

    def get_apps_count(self) -> int:
        """¾»иµв¾ голосовые."""
        return len(self.apps)
