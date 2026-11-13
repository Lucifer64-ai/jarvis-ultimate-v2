"""
µ½µ´¶µ º¾½µº° JARVIS
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


class ContextManager:
    """£¿°²»µ½¸µ º¾½µº¾¼ °·³¾²¾° ¸ ¾¾½¸."""

    def __init__(self, brain):
        self.brain = brain
        self.context_file = Path("data/context.json")
        self.context_file.parent.mkdir(exist_ok=True)
        
        self.context: Dict = self._load_context()
        self.conversation_history: List[Dict] = []
        self.max_history = 50

    def _load_context(self) -> Dict:
        """°³·º° º¾½µº° ¸· °¹»°."""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.brain.logger.error(f"¸±º° ·°³·º¸ º¾½µº°: {e}")
        
        return {
            "user_preferences": {},
            "session_start": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }

    def _save_context(self):
        """¡¾°½µ½¸µ º¾½µº°."""
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.brain.logger.error(f"¸±º° ¾°½µ½¸ º¾½µº°: {e}")

    def update(self, key: str, value):
        """±½¾²»µ½¸µ º¾½µº°."""
        self.context[key] = value
        self.context["last_activity"] = datetime.now().isoformat()
        self._save_context()

    def get(self, key: str, default=None):
        """¾»µ½¸µ ·½°µ½¸ ¸· º¾½µº°."""
        return self.context.get(key, default)

    def add_to_history(self, role: str, content: str):
        """¾±°²»µ½¸µ ² ¸¾¸ °·³¾²¾°."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # ³°½¸µ½¸µ ¸¾¸¸
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_history(self, limit: int = 10) -> List[Dict]:
        """¾»µ½¸µ ¸¾¸¸ °·³¾²¾°."""
        return self.conversation_history[-limit:]

    def clear_history(self):
        """¸º° ¸¾¸¸."""
        self.conversation_history = []

    def get_system_context(self) -> Dict:
        """¾»µ½¸µ ¸µ¼½¾³¾ º¾½µº°."""
        import psutil
        
        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "time": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    def set_user_preference(self, key: str, value):
        """£°½¾²º° ¿¾»·¾²°µ»º¸ ¿µ´¿¾µ½¸¹."""
        if "user_preferences" not in self.context:
            self.context["user_preferences"] = {}
        
        self.context["user_preferences"][key] = value
        self._save_context()

    def get_user_preference(self, key: str, default=None):
        """¾»µ½¸µ ¿¾»·¾²°µ»º¸ ¿µ´¿¾µ½¸¹."""
        return self.context.get("user_preferences", {}).get(key, default)
