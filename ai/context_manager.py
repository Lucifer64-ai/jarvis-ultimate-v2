"""
Менеджер контекста JARVIS
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


class ContextManager:
    """Управление контекстом разговоров и состояний."""

    def __init__(self, brain):
        self.brain = brain
        self.context_file = Path("data/context.json")
        self.context_file.parent.mkdir(exist_ok=True)

        self.context: Dict = self._load_context()
        self.conversation_history: List[Dict] = []
        self.max_history = 50

    def _load_context(self) -> Dict:
        """Загрузка контекста из файла."""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.brain.logger.error(f"Ошибка загрузки контекста: {e}")

        return {
            "user_preferences": {},
            "session_start": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }

    def _save_context(self):
        """Сохранение контекста."""
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.brain.logger.error(f"Ошибка сохранения контекста: {e}")

    def update(self, key: str, value):
        """Обновление контекста."""
        self.context[key] = value
        self.context["last_activity"] = datetime.now().isoformat()
        self._save_context()

    def get(self, key: str, default=None):
        """Получение значения из контекста."""
        return self.context.get(key, default)

    def add_to_history(self, role: str, content: str):
        """Добавление сообщения в историю разговора."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Ограничиваем размер истории
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_conversation_context(self, last_n: int = 10) -> List[Dict]:
        """Получение последних N сообщений для контекста."""
        return self.conversation_history[-last_n:]

    def clear_history(self):
        """Очистка истории разговора."""
        self.conversation_history.clear()
        self.brain.logger.info("История разговора очищена")

    def get_user_preference(self, key: str, default=None):
        """Получение пользовательских настроек."""
        return self.context.get("user_preferences", {}).get(key, default)

    def set_user_preference(self, key: str, value):
        """Установка пользовательских настроек."""
        if "user_preferences" not in self.context:
            self.context["user_preferences"] = {}
        self.context["user_preferences"][key] = value
        self._save_context()
        self.brain.logger.info(f"Сохранена настройка: {key}={value}")
