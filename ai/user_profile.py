"""
¾¸» ¿¾»·¾²°µ» JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter


class UserProfile:
    """£¿°²»µ½¸µ ¿¾¸»µ¼ ¸ ¿µ´¿¾µ½¸¼¸ ¿¾»·¾²°µ»."""

    def __init__(self, brain):
        self.brain = brain
        self.profile_file = Path("data/user_profile.json")
        self.profile_file.parent.mkdir(exist_ok=True)
        self.profile: Dict = self._load_profile()
        self.command_history: List[Dict] = []

    def _load_profile(self) -> Dict:
        """°³·º° ¿¾¸»."""
        if self.profile_file.exists():
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "name": None,
            "preferred_name": "",
            "language": "ru",
            "created": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "preferences": {
                "voice_rate": 180,
                "voice_volume": 1.0,
                "hud_enabled": True,
                "notifications": True
            },
            "statistics": {
                "total_commands": 0,
                "favorite_commands": [],
                "active_hours": [],
                "most_used_modules": []
            }
        }

    def _save_profile(self):
        """¡¾°½µ½¸µ ¿¾¸»."""
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)

    def set_name(self, name: str) -> Dict:
        """£°½¾²º° ¸¼µ½¸ ¿¾»·¾²°µ»."""
        self.profile["name"] = name
        self._save_profile()
        return {"status": "ok", "message": f"¼ °½¾²»µ½¾: {name}"}

    def set_preferred_name(self, preferred: str) -> Dict:
        """£°½¾²º° ¿µ´¿¾¸µ»½¾³¾ ¾±°µ½¸."""
        self.profile["preferred_name"] = preferred
        self._save_profile()
        return {"status": "ok", "message": f"´ ¾±°° º ²°¼: {preferred}"}

    def get_greeting(self) -> str:
        """¾»µ½¸µ ¿¸²µ²¸."""
        preferred = self.profile.get("preferred_name", "")
        name = self.profile.get("name")
        
        if name:
            return f"´°²²¹µ, {name}.  °´ ²° ²¸´µ, {preferred}."
        return f"´°²²¹µ, {preferred}."

    def update_activity(self):
        """±½¾²»µ½¸µ ¿¾»µ´½µ¹ °º¸²½¾¸."""
        self.profile["last_active"] = datetime.now().isoformat()
        self._save_profile()

    def log_command(self, command: str, module: str = "unknown"):
        """¾³¸¾²°½¸µ º¾¼°½´."""
        self.command_history.append({
            "command": command,
            "module": module,
            "timestamp": datetime.now().isoformat()
        })
        
        # ³°½¸µ½¸µ ¸¾¸¸
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]
        
        # ±½¾²»µ½¸µ °¸¸º¸
        self.profile["statistics"]["total_commands"] += 1
        self._update_statistics()
        self._save_profile()

    def _update_statistics(self):
        """±½¾²»µ½¸µ °¸¸º¸."""
        if not self.command_history:
            return
        
        # ¡°¼µ °µ º¾¼°½´
        commands = [entry["command"] for entry in self.command_history[-100:]]
        command_counts = Counter(commands)
        self.profile["statistics"]["favorite_commands"] = [
            {"command": cmd, "count": count}
            for cmd, count in command_counts.most_common(5)
        ]
        
        # ¡°¼µ ¸¿¾»·µ¼µ ¼¾´»¸
        modules = [entry["module"] for entry in self.command_history[-100:]]
        module_counts = Counter(modules)
        self.profile["statistics"]["most_used_modules"] = [
            {"module": mod, "count": count}
            for mod, count in module_counts.most_common(5)
        ]
        
        # º¸²½µ °
        hours = []
        for entry in self.command_history[-100:]:
            try:
                dt = datetime.fromisoformat(entry["timestamp"])
                hours.append(dt.hour)
            except:
                pass
        
        if hours:
            hour_counts = Counter(hours)
            self.profile["statistics"]["active_hours"] = [
                {"hour": hour, "count": count}
                for hour, count in hour_counts.most_common(3)
            ]

    def set_preference(self, key: str, value: Any) -> Dict:
        """£°½¾²º° ¿µ´¿¾µ½¸."""
        self.profile["preferences"][key] = value
        self._save_profile()
        return {"status": "ok", "message": f"µ´¿¾µ½¸µ '{key}' °½¾²»µ½¾"}

    def get_preference(self, key: str, default: Any = None) -> Any:
        """¾»µ½¸µ ¿µ´¿¾µ½¸."""
        return self.profile["preferences"].get(key, default)

    def get_profile(self) -> Dict:
        """¾»µ½¸µ ¿¾»½¾³¾ ¿¾¸»."""
        return self.profile

    def get_statistics(self) -> Dict:
        """¾»µ½¸µ °¸¸º¸."""
        return self.profile.get("statistics", {})

    def reset_statistics(self) -> Dict:
        """¡±¾ °¸¸º¸."""
        self.profile["statistics"] = {
            "total_commands": 0,
            "favorite_commands": [],
            "active_hours": [],
            "most_used_modules": []
        }
        self.command_history = []
        self._save_profile()
        return {"status": "ok", "message": "¡°¸¸º° ±¾µ½°"}
