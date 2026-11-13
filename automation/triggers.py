"""
¡иµ¼° и³³µ¾в JARVIS
"""

from typing import Dict, List, Callable
import threading
import time


class TriggerManager:
    """£¿°в»µ½иµ и³³µ°¼и."""

    def __init__(self, brain):
        self.brain = brain
        self.triggers: Dict[str, Dict] = {}
        self.running = False

    def add_trigger(self, name: str, condition: Callable, action: Callable):
        """¾±°ви и³³µ."""
        self.triggers[name] = {
            "condition": condition,
            "action": action,
            "active": True
        }
        self.brain.logger.info(f"¢и³³µ '{name}' ´¾±°в»µ½")
        return {"status": "ok", "name": name}

    def remove_trigger(self, name: str):
        """£´°»и и³³µ."""
        if name in self.triggers:
            del self.triggers[name]
            return {"status": "ok"}
        return {"status": "error", "message": "¢и³³µ ни ½°¹´µ½"}

    def list_triggers(self) -> List[str]:
        """¡¿и¾º и³³µ¾в."""
        return list(self.triggers.keys())

    def start(self):
        """°¿º ¿¾вµºи и³³µ¾в."""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        """½¾в½¾¹ иº» ¿¾вµºи и³³µ¾в."""
        while self.running:
            for name, trigger in self.triggers.items():
                if not trigger["active"]:
                    continue
                
                try:
                    if trigger["condition"]():
                        self.brain.logger.info(f"¢и³³µ '{name}' °±¾°»")
                        trigger["action"]()
                except Exception as e:
                    self.brain.logger.error(f"агента и³³µ° '{name}': {e}")
            
            time.sleep(5)

    def stop(self):
        """°½¾вº° ¿¾вµºи и³³µ¾в."""
        self.running = False
