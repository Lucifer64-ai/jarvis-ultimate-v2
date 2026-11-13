"""
¡¸µ¼° ¸³³µ¾² JARVIS
"""

from typing import Dict, List, Callable
import threading
import time


class TriggerManager:
    """£¿°²»µ½¸µ ¸³³µ°¼¸."""

    def __init__(self, brain):
        self.brain = brain
        self.triggers: Dict[str, Dict] = {}
        self.running = False

    def add_trigger(self, name: str, condition: Callable, action: Callable):
        """¾±°²¸ ¸³³µ."""
        self.triggers[name] = {
            "condition": condition,
            "action": action,
            "active": True
        }
        self.brain.logger.info(f"¢¸³³µ '{name}' ´¾±°²»µ½")
        return {"status": "ok", "name": name}

    def remove_trigger(self, name: str):
        """£´°»¸ ¸³³µ."""
        if name in self.triggers:
            del self.triggers[name]
            return {"status": "ok"}
        return {"status": "error", "message": "¢¸³³µ ½µ ½°¹´µ½"}

    def list_triggers(self) -> List[str]:
        """¡¿¸¾º ¸³³µ¾²."""
        return list(self.triggers.keys())

    def start(self):
        """°¿º ¿¾²µº¸ ¸³³µ¾²."""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        """½¾²½¾¹ ¸º» ¿¾²µº¸ ¸³³µ¾²."""
        while self.running:
            for name, trigger in self.triggers.items():
                if not trigger["active"]:
                    continue
                
                try:
                    if trigger["condition"]():
                        self.brain.logger.info(f"¢¸³³µ '{name}' °±¾°»")
                        trigger["action"]()
                except Exception as e:
                    self.brain.logger.error(f"¸±º° ¸³³µ° '{name}': {e}")
            
            time.sleep(5)

    def stop(self):
        """°½¾²º° ¿¾²µº¸ ¸³³µ¾²."""
        self.running = False
