"""
Система алиасов JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class AliasSystem:
    """Управление пользовательскими алиасами для команд."""

    def __init__(self, brain):
        self.brain = brain
        self.aliases_file = Path("data/aliases.json")
        self.aliases_file.parent.mkdir(exist_ok=True)
        self.aliases: Dict[str, str] = self._load_aliases()

    def _load_aliases(self) -> Dict[str, str]:
        """Загрузка алиасов из файла."""
        if self.aliases_file.exists():
            with open(self.aliases_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_aliases(self):
        """Сохранение алиасов."""
        with open(self.aliases_file, 'w', encoding='utf-8') as f:
            json.dump(self.aliases, f, ensure_ascii=False, indent=2)

    def add_alias(self, alias: str, command: str) -> Dict:
        """Добавление нового алиаса."""
        alias_lower = alias.lower().strip()
        command_lower = command.lower().strip()

        self.aliases[alias_lower] = command_lower
        self._save_aliases()

        self.brain.logger.info(f"Добавлен алиас: '{alias}' -> '{command}'")
        return {
            "status": "ok",
            "alias": alias_lower,
            "command": command_lower,
            "message": f"Алиас '{alias}' сохранён"
        }

    def remove_alias(self, alias: str) -> Dict:
        """Удаление алиаса."""
        alias_lower = alias.lower().strip()

        if alias_lower in self.aliases:
            del self.aliases[alias_lower]
            self._save_aliases()
            self.brain.logger.info(f"Удалён алиас: '{alias}'")
            return {
                "status": "ok",
                "message": f"Алиас '{alias}' удалён"
            }

        return {
            "status": "error",
            "message": f"Алиас '{alias}' не найден"
        }

    def resolve(self, text: str) -> str:
        """Разрешение алиаса в команду."""
        text_lower = text.lower().strip()

        if text_lower in self.aliases:
            resolved = self.aliases[text_lower]
            self.brain.logger.info(f"Алиас разрешён: '{text}' -> '{resolved}'")
            return resolved

        return text

    def list_aliases(self) -> List[Dict]:
        """Список всех алиасов."""
        return [
            {"alias": alias, "command": command}
            for alias, command in self.aliases.items()
        ]

    def clear_all(self) -> Dict:
        """Очистка всех алиасов."""
        count = len(self.aliases)
        self.aliases.clear()
        self._save_aliases()
        self.brain.logger.info(f"Удалено алиасов: {count}")
        return {
            "status": "ok",
            "message": f"Удалено {count} алиасов"
        }
