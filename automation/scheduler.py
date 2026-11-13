"""
»°½и¾виº ·°´° JARVIS
"""

import schedule
import time
import threading
from typing import Dict, List, Callable
from datetime import datetime


class TaskScheduler:
    """»°½и¾виº ·°´°."""

    def __init__(self, brain):
        self.brain = brain
        self.tasks: Dict[str, Dict] = {}
        self.running = False

    def add_task(self, name: str, time_str: str, callback: Callable, days: List[str] = None):
        """¾±°ви ·°´°."""
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
        
        self.brain.logger.info(f"°´°° '{name}' ´¾±°в»µ½° ½° {time_str}")
        return {"status": "ok", "name": name}

    def remove_task(self, name: str):
        """£´°»и ·°´°."""
        if name in self.tasks:
            schedule.clear(name)
            del self.tasks[name]
            self.brain.logger.info(f"°´°° '{name}' ´°»µ½°")
            return {"status": "ok"}
        return {"status": "error", "message": "°´°° ни ½°¹´µ½°"}

    def list_tasks(self) -> List[Dict]:
        """¡¿и¾º ·°´°."""
        return [
            {"name": name, **data}
            for name, data in self.tasks.items()
        ]

    def start(self):
        """°¿º ¿»°½и¾виº°."""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        """½¾в½¾¹ иº» ¿»°½и¾виº°."""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        """°½¾вº° ¿»°½и¾виº°."""
        self.running = False
        schedule.clear()
