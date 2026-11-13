"""
¾и» ¿¾»·¾в°µ» JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter


class UserProfile:
    """£¿°в»µ½иµ ¿¾и»µ¼ и ¿µ´¿¾µ½и¼и ¿¾»·¾в°µ»."""

    def __init__(self, brain):
        self.brain = brain
        self.profile_file = Path("data/user_profile.json")
        self.profile_file.parent.mkdir(exist_ok=True)
        self.profile: Dict = self._load_profile()
        self.command_history: List[Dict] = []

    def _load_profile(self) -> Dict:
        """°³·º° ¿¾и»."""
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
        """¡¾°ни½иµ ¿¾и»."""
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)

    def set_name(self, name: str) -> Dict:
        """£°½¾вº° и¼µ½и ¿¾»·¾в°µ»."""
        self.profile["name"] = name
        self._save_profile()
        return {"status": "ok", "message": f"¼ °½¾в»µ½¾: {name}"}

    def set_preferred_name(self, preferred: str) -> Dict:
        """£°½¾вº° ¿µ´¿¾иµ»½¾³¾ ¾±°µ½и."""
        self.profile["preferred_name"] = preferred
        self._save_profile()
        return {"status": "ok", "message": f"´ ¾±°° º в°¼: {preferred}"}

    def get_greeting(self) -> str:
        """¾»µ½иµ ¿ивµви."""
        preferred = self.profile.get("preferred_name", "")
        name = self.profile.get("name")
        
        if name:
            return f"´°вв¹µ, {name}.  °´ в° ви´µ, {preferred}."
        return f"´°вв¹µ, {preferred}."

    def update_activity(self):
        """±½¾в»µ½иµ ¿¾»µ´ни¹ °ºив½¾и."""
        self.profile["last_active"] = datetime.now().isoformat()
        self._save_profile()

    def log_command(self, command: str, module: str = "unknown"):
        """¾³и¾в°½иµ º¾¼°½´."""
        self.command_history.append({
            "command": command,
            "module": module,
            "timestamp": datetime.now().isoformat()
        })
        
        # ³°½иµ½иµ и¾ии
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]
        
        # ±½¾в»µ½иµ °ииºи
        self.profile["statistics"]["total_commands"] += 1
        self._update_statistics()
        self._save_profile()

    def _update_statistics(self):
        """±½¾в»µ½иµ °ииºи."""
        if not self.command_history:
            return
        
        # ¡°¼µ °µ º¾¼°½´
        commands = [entry["command"] for entry in self.command_history[-100:]]
        command_counts = Counter(commands)
        self.profile["statistics"]["favorite_commands"] = [
            {"command": cmd, "count": count}
            for cmd, count in command_counts.most_common(5)
        ]
        
        # ¡°¼µ и¿¾»·µ¼µ ¼¾´»и
        modules = [entry["module"] for entry in self.command_history[-100:]]
        module_counts = Counter(modules)
        self.profile["statistics"]["most_used_modules"] = [
            {"module": mod, "count": count}
            for mod, count in module_counts.most_common(5)
        ]
        
        # ºив½µ °
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
        """£°½¾вº° ¿µ´¿¾µ½и."""
        self.profile["preferences"][key] = value
        self._save_profile()
        return {"status": "ok", "message": f"µ´¿¾µ½иµ '{key}' °½¾в»µ½¾"}

    def get_preference(self, key: str, default: Any = None) -> Any:
        """¾»µ½иµ ¿µ´¿¾µ½и."""
        return self.profile["preferences"].get(key, default)

    def get_profile(self) -> Dict:
        """¾»µ½иµ ¿¾»½¾³¾ ¿¾и»."""
        return self.profile

    def get_statistics(self) -> Dict:
        """¾»µ½иµ °ииºи."""
        return self.profile.get("statistics", {})

    def reset_statistics(self) -> Dict:
        """¡±¾ °ииºи."""
        self.profile["statistics"] = {
            "total_commands": 0,
            "favorite_commands": [],
            "active_hours": [],
            "most_used_modules": []
        }
        self.command_history = []
        self._save_profile()
        return {"status": "ok", "message": "¡°ииº° ±¾µ½°"}
