"""
Планировщик задач JARVIS
"""

import schedule
import time
import threading
from typing import Dict, List, Callable
from datetime import datetime


class TaskScheduler:
    """Планировщик задач."""

    def __init__(self, brain):
        self.brain = brain
        self.tasks: Dict[str, Dict] = {}
        self.running = False

    def add_task(self, name: str, time_str: str, callback: Callable, days: List[str] = None):
        """Добавить задачу."""
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

        self.brain.logger.info(f"Задача '{name}' добавлена на {time_str}")
        return {"status": "ok", "name": name}

    def remove_task(self, name: str):
        """Удалить задачу."""
        if name in self.tasks:
            schedule.clear(name)
            del self.tasks[name]
            self.brain.logger.info(f"Задача '{name}' удалена")
            return {"status": "ok"}
        return {"status": "error", "message": "Задача не найдена"}

    def list_tasks(self) -> List[Dict]:
        """Список задач."""
        return [
            {"name": name, **data}
            for name, data in self.tasks.items()
        ]

    def start(self):
        """Запуск планировщика."""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        """Основной цикл планировщика."""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        """Остановка планировщика."""
        self.running = False
        schedule.clear()
