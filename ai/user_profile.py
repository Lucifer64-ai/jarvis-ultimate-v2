"""
Профиль пользователя JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter


class UserProfile:
    """Управление профилем и предпочтениями пользователя."""

    def __init__(self, brain):
        self.brain = brain
        self.profile_file = Path("data/user_profile.json")
        self.profile_file.parent.mkdir(exist_ok=True)
        self.profile: Dict = self._load_profile()
        self.command_history: List[Dict] = []

    def _load_profile(self) -> Dict:
        """Загрузка профиля."""
        if self.profile_file.exists():
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "name": None,
            "preferred_name": "сэр",
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
        """Сохранение профиля."""
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)

    def set_name(self, name: str) -> Dict:
        """Установка имени пользователя."""
        self.profile["name"] = name
        self._save_profile()
        return {"status": "ok", "message": f"Имя установлено: {name}"}

    def set_preferred_name(self, preferred: str) -> Dict:
        """Установка предпочтительного обращения."""
        self.profile["preferred_name"] = preferred
        self._save_profile()
        return {"status": "ok", "message": f"Буду обращаться к вам: {preferred}"}

    def get_greeting(self) -> str:
        """Приветствие пользователя."""
        preferred = self.profile.get("preferred_name", "сэр")
        name = self.profile.get("name")

        if name:
            return f"Добрый день, {name}. Рад вас видеть, {preferred}."
        return f"Добрый день, {preferred}."

    def update_activity(self):
        """Обновление последней активности."""
        self.profile["last_active"] = datetime.now().isoformat()
        self._save_profile()

    def log_command(self, command: str, module: str = "unknown"):
        """Логирование команд."""
        self.command_history.append({
            "command": command,
            "module": module,
            "timestamp": datetime.now().isoformat()
        })

        # Ограничение истории
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]

        # Обновление статистики
        self.profile["statistics"]["total_commands"] += 1
        self._update_statistics()
        self._save_profile()

    def _update_statistics(self):
        """Обновление статистики."""
        if not self.command_history:
            return

        # Самые частые команды
        commands = [entry["command"] for entry in self.command_history[-100:]]
        command_counts = Counter(commands)
        self.profile["statistics"]["favorite_commands"] = [
            {"command": cmd, "count": count}
            for cmd, count in command_counts.most_common(5)
        ]

        # Самые используемые модули
        modules = [entry["module"] for entry in self.command_history[-100:]]
        module_counts = Counter(modules)
        self.profile["statistics"]["most_used_modules"] = [
            {"module": mod, "count": count}
            for mod, count in module_counts.most_common(5)
        ]

        # Активные часы
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
        """Установка предпочтения."""
        self.profile["preferences"][key] = value
        self._save_profile()
        return {"status": "ok", "message": f"Предпочтение '{key}' установлено"}

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Получение предпочтения."""
        return self.profile["preferences"].get(key, default)

    def get_profile(self) -> Dict:
        """Получение полного профиля."""
        return self.profile

    def get_statistics(self) -> Dict:
        """Получение статистики."""
        return self.profile.get("statistics", {})

    def reset_statistics(self) -> Dict:
        """Сброс статистики."""
        self.profile["statistics"] = {
            "total_commands": 0,
            "favorite_commands": [],
            "active_hours": [],
            "most_used_modules": []
        }
        self.command_history = []
        self._save_profile()
        return {"status": "ok", "message": "Статистика сброшена"}
