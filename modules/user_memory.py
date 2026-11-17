"""
Модуль памяти пользователя JARVIS (стиль Железного Человека)
- Многоязычная поддержка (русский / английский)
- Хранение предпочтений пользователя
- История разговоров и команд
- Персонализация обращения (Сэр, сэр, sir)
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class UserMemory:
    """Модуль памяти пользователя и локализации для JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Конфигурация
        config = brain.config.get("user_memory", {})
        self.enabled = config.get("enabled", True)
        self.memory_file = Path(config.get("memory_file", "data/user_memory.json"))
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        # Поддерживаемые языки
        self.supported_languages = {
            "ru": "Русский",
            "en": "English"
        }

        # Текущий язык
        self.current_language = config.get("language", "ru")

        # Данные пользователя
        self.user_data: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []
        self.max_history = config.get("max_history", 100)

        # Шаблоны ответов на разных языках
        self.templates = {
            "ru": {
                "greeting": "Здравствуйте, {name}. Чем могу помочь?",
                "goodbye": "До свидания, {name}. Жду ваших команд.",
                "not_understood": "Извините, я не понял команду. Повторите, пожалуйста.",
                "processing": "Обрабатываю запрос, {name}.",
                "system_ready": "Система готова к работе.",
                "sir_address": "Сэр",
            },
            "en": {
                "greeting": "Hello, {name}. How can I help you?",
                "goodbye": "Goodbye, {name}. Awaiting your commands.",
                "not_understood": "Sorry, I didn't understand that command. Please repeat.",
                "processing": "Processing your request, {name}.",
                "system_ready": "System ready.",
                "sir_address": "Sir",
            }
        }

        # Загрузка данных
        self._load_memory()

    def _load_memory(self):
        """Загрузка памяти пользователя из файла."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.user_data = data.get("user_data", {})
                self.conversation_history = data.get("conversation_history", [])
                self.current_language = data.get("language", self.current_language)
                self.logger.info("Память пользователя загружена")
            except Exception as e:
                self.logger.error(f"Ошибка загрузки памяти: {e}")

    def _save_memory(self):
        """Сохранение памяти пользователя в файл."""
        try:
            data = {
                "user_data": self.user_data,
                "conversation_history": self.conversation_history[-self.max_history:],
                "language": self.current_language,
                "updated": datetime.now().isoformat()
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения памяти: {e}")

    # === Язык и локализация ===

    def set_language(self, language_code: str) -> Dict:
        """Установить язык интерфейса."""
        if language_code not in self.supported_languages:
            return {
                "status": "error",
                "message": f"Язык '{language_code}' не поддерживается. Доступные: {list(self.supported_languages.keys())}"
            }

        self.current_language = language_code
        self._save_memory()

        return {
            "status": "ok",
            "message": f"Язык изменен на: {self.supported_languages[language_code]}",
            "language": language_code
        }

    def get_language(self) -> str:
        """Получить текущий язык."""
        return self.current_language

    def get_template(self, key: str, **kwargs) -> str:
        """Получить локализованную строку по ключу."""
        lang_templates = self.templates.get(self.current_language, self.templates["ru"])
        template = lang_templates.get(key, key)
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template

    def get_sir_address(self) -> str:
        """Получить обращение к пользователю (Сэр / Sir)."""
        return self.get_template("sir_address")

    # === Данные пользователя ===

    def set_preference(self, key: str, value: Any) -> Dict:
        """Установить предпочтение пользователя."""
        self.user_data[key] = value
        self._save_memory()
        return {"status": "ok", "message": f"Предпочтение '{key}' установлено"}

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Получить предпочтение пользователя."""
        return self.user_data.get(key, default)

    def remove_preference(self, key: str) -> Dict:
        """Удалить предпочтение пользователя."""
        if key in self.user_data:
            del self.user_data[key]
            self._save_memory()
            return {"status": "ok", "message": f"Предпочтение '{key}' удалено"}
        return {"status": "error", "message": f"Предпочтение '{key}' не найдено"}

    def list_preferences(self) -> Dict:
        """Список всех предпочтений."""
        return {
            "status": "ok",
            "preferences": self.user_data
        }

    # === История разговоров ===

    def add_conversation(self, user_input: str, jarvis_response: str, intent: Optional[str] = None) -> None:
        """Добавить запись в историю разговоров."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "jarvis_response": jarvis_response,
            "intent": intent
        }
        self.conversation_history.append(entry)

        # Ограничиваем размер истории
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        self._save_memory()

    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Получить историю разговоров."""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history

    def clear_history(self) -> Dict:
        """Очистить историю разговоров."""
        count = len(self.conversation_history)
        self.conversation_history = []
        self._save_memory()
        return {"status": "ok", "message": f"Очищено {count} записей истории"}

    # === Статус ===

    def get_status(self) -> Dict:
        """Получить статус модуля памяти."""
        return {
            "status": "ok",
            "enabled": self.enabled,
            "language": self.current_language,
            "supported_languages": self.supported_languages,
            "preferences_count": len(self.user_data),
            "conversation_count": len(self.conversation_history),
            "memory_file": str(self.memory_file)
        }
