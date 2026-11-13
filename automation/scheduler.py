"""
»°½¸¾²¸º ·°´° JARVIS
"""

import schedule
import time
import threading
from typing import Dict, List, Callable
from datetime import datetime


class TaskScheduler:
    """»°½¸¾²¸º ·°´°."""

    def __init__(self, brain):
        self.brain = brain
        self.tasks: Dict[str, Dict] = {}
        self.running = False

    def add_task(self, name: str, time_str: str, callback: Callable, days: List[str] = None):
        """¾±°²¸ ·°´°."""
        job = schedule.every()
        
        if days:
            for day in days:
                getattr(job, day.lower()).at(time_str).do(callback)
        else:
            job.every().day.at(time_str).do(callback)
        
        self.tasks[name] = {
            "time": time_str,
            "days": days or ["every day"],
            "callback": callback.__name__,
            "created": datetime.now().isoformat()
        }
        
        self.brain.logger.info(f"°´°° '{name}' ´¾±°²»µ½° ½° {time_str}")
        return {"status": "ok", "name": name}

    def remove_task(self, name: str):
        """£´°»¸ ·°´°."""
        if name in self.tasks:
            schedule.clear(name)
            del self.tasks[name]
            self.brain.logger.info(f"°´°° '{name}' ´°»µ½°")
            return {"status": "ok"}
        return {"status": "error", "message": "°´°° ½µ ½°¹´µ½°"}

    def list_tasks(self) -> List[Dict]:
        """¡¿¸¾º ·°´°."""
        return [
            {"name": name, **data}
            for name, data in self.tasks.items()
        ]

    def start(self):
        """°¿º ¿»°½¸¾²¸º°."""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        """½¾²½¾¹ ¸º» ¿»°½¸¾²¸º°."""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        """°½¾²º° ¿»°½¸¾²¸º°."""
        self.running = False
        schedule.clear()
