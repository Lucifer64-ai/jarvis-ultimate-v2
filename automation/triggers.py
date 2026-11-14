"""
Система триггеров JARVIS
"""

from typing import Dict, List, Callable
import threading
import time


class TriggerManager:
    """Управление триггерами."""

    def __init__(self, brain):
        self.brain = brain
        self.triggers: Dict[str, Dict] = {}
        self.running = False

    def add_trigger(self, name: str, condition: Callable, action: Callable):
        """Добавить триггер."""
        self.triggers[name] = {
            "condition": condition,
            "action": action,
            "active": True
        }
        self.brain.logger.info(f"Триггер '{name}' добавлен")
        return {"status": "ok", "name": name}

    def remove_trigger(self, name: str):
        """Удалить триггер."""
        if name in self.triggers:
            del self.triggers[name]
            return {"status": "ok"}
        return {"status": "error", "message": "Триггер не найден"}

    def list_triggers(self) -> List[str]:
        """Список триггеров."""
        return list(self.triggers.keys())

    def start(self):
        """Запуск проверки триггеров."""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        """Основной цикл проверки триггеров."""
        while self.running:
            for name, trigger in self.triggers.items():
                if not trigger["active"]:
                    continue

                try:
                    if trigger["condition"]():
                        self.brain.logger.info(f"Триггер '{name}' сработал")
                        trigger["action"]()
                except Exception as e:
                    self.brain.logger.error(f"Ошибка триггера '{name}': {e}")

            time.sleep(5)

    def stop(self):
        """Остановка проверки триггеров."""
        self.running = False
