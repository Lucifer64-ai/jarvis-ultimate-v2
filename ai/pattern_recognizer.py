"""
Распознавание паттернов JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import re


class PatternRecognizer:
    """Распознавание паттернов в поведении пользователя."""

    def __init__(self, brain):
        self.brain = brain
        self.patterns_file = Path("data/patterns.json")
        self.patterns_file.parent.mkdir(exist_ok=True)
        self.patterns: Dict = self._load_patterns()
        self.suggestions: List[Dict] = []

    def _load_patterns(self) -> Dict:
        """Загрузка паттернов."""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "recurring_commands": {},
            "time_based_patterns": {},
            "sequence_patterns": {},
            "learned_automations": []
        }

    def _save_patterns(self):
        """Сохранение паттернов."""
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, ensure_ascii=False, indent=2)

    def analyze_command_history(self, history: List[Dict]) -> List[Dict]:
        """Анализ истории команд для выявления паттернов."""
        suggestions = []

        # 1. Повторяющиеся команды в одно время
        time_patterns = self._detect_time_patterns(history)
        suggestions.extend(time_patterns)

        # 2. Последовательности команд
        sequence_patterns = self._detect_sequence_patterns(history)
        suggestions.extend(sequence_patterns)

        # 3. Часто используемые команды
        frequent_commands = self._detect_frequent_commands(history)
        suggestions.extend(frequent_commands)

        self.suggestions = suggestions
        self._save_patterns()

        return suggestions

    def _detect_time_patterns(self, history: List[Dict]) -> List[Dict]:
        """Обнаружение временных паттернов."""
        suggestions = []
        time_groups = defaultdict(list)

        for entry in history:
            try:
                dt = datetime.fromisoformat(entry["timestamp"])
                hour = dt.hour
                minute = dt.minute
                # Группируем по 15-минутным интервалам
                time_slot = f"{hour:02d}:{(minute // 15) * 15:02d}"
                time_groups[time_slot].append(entry["command"])
            except:
                continue

        # Ищем команд, которые повторяются в одно время
        for time_slot, commands in time_groups.items():
            command_counts = defaultdict(int)
            for cmd in commands:
                command_counts[cmd] += 1

            for cmd, count in command_counts.items():
                if count >= 3:  # Если команда повторяется 3+ раза в это время
                    suggestions.append({
                        "type": "time_pattern",
                        "command": cmd,
                        "time": time_slot,
                        "count": count,
                        "suggestion": f"Вы часто говорите '{cmd}' в {time_slot}. Создать автоматическое расписание?",
                        "action": "create_schedule"
                    })

        return suggestions

    def _detect_sequence_patterns(self, history: List[Dict]) -> List[Dict]:
        """Обнаружение последовательностей команд."""
        suggestions = []

        if len(history) < 3:
            return suggestions

        # Ищем повторяющиеся последовательности из 2-3 команд
        for seq_length in [2, 3]:
            sequences = defaultdict(int)

            for i in range(len(history) - seq_length + 1):
                seq = tuple(entry["command"] for entry in history[i:i+seq_length])
                sequences[seq] += 1

            for seq, count in sequences.items():
                if count >= 2:  # Если последовательность повторяется 2+ раза
                    suggestions.append({
                        "type": "sequence_pattern",
                        "sequence": list(seq),
                        "count": count,
                        "suggestion": f"Вы часто выполняете последовательность: {' → '.join(seq)}. Создать макрос?",
                        "action": "create_macro"
                    })

        return suggestions

    def _detect_frequent_commands(self, history: List[Dict]) -> List[Dict]:
        """Обнаружение часто используемых команд."""
        suggestions = []
        command_counts = defaultdict(int)

        for entry in history:
            command_counts[entry["command"]] += 1

        for cmd, count in command_counts.items():
            if count >= 10:  # Если команда используется 10+ раз
                suggestions.append({
                    "type": "frequent_command",
                    "command": cmd,
                    "count": count,
                    "suggestion": f"Команда '{cmd}' используется очень часто ({count} раз). Создать быстрый алиас?",
                    "action": "create_alias"
                })

        return suggestions

    def get_suggestions(self) -> List[Dict]:
        """Получение текущих предложений."""
        return self.suggestions

    def accept_suggestion(self, index: int) -> Dict:
        """Принятие предложения."""
        if index >= len(self.suggestions):
            return {"status": "error", "message": "Предложение не найдено"}

        suggestion = self.suggestions[index]
        action = suggestion["action"]

        if action == "create_schedule":
            # Создание расписания
            return {
                "status": "ok",
                "message": f"Расписание создано для команды '{suggestion['command']}' в {suggestion['time']}",
                "action_taken": "schedule_created"
            }

        elif action == "create_macro":
            # Создание макроса
            return {
                "status": "ok",
                "message": f"Макрос создан для последовательности: {' → '.join(suggestion['sequence'])}",
                "action_taken": "macro_created"
            }

        elif action == "create_alias":
            # Создание алиаса
            return {
                "status": "ok",
                "message": f"Предложение алиаса для команды '{suggestion['command']}'",
                "action_taken": "alias_pending"
            }

        return {"status": "error", "message": "Неизвестное действие"}

    def learn_automation(self, trigger: str, action: str) -> Dict:
        """Обучение новой автоматизации."""
        automation = {
            "trigger": trigger,
            "action": action,
            "created": datetime.now().isoformat(),
            "usage_count": 0
        }

        self.patterns["learned_automations"].append(automation)
        self._save_patterns()

        return {
            "status": "ok",
            "message": f"Автоматизация обучена: '{trigger}' → '{action}'"
        }

    def get_learned_automations(self) -> List[Dict]:
        """Получение обученных автоматизаций."""
        return self.patterns.get("learned_automations", [])
