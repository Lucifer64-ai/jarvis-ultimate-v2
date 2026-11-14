"""
Улучшение распознавания речи JARVIS
"""

import re
from typing import List, Dict


class VoiceEnhancer:
    """Улучшение качества распознавания речи."""

    def __init__(self, brain):
        self.brain = brain
        self.corrections = self._load_corrections()

    def _load_corrections(self) -> Dict[str, str]:
        """Загрузка словаря исправлений."""
        return {
            # Частые ошибки распознавания
            "джавис": "джарвис",
            "jarvis": "джарвис",
            "жарвис": "джарвис",
            "ярвис": "джарвис",

            # Системные команды
            "включи": "включи",
            "выключи": "выключи",
            "открой": "открой",
            "закрой": "закрой",
            "покажи": "покажи",

            # Приложения
            "блокнот": "блокнот",
            "notepad": "блокнот",
            "калькулятор": "калькулятор",
            "ютуб": "youtube",
            "youtube": "youtube",
            "гитхаб": "github",
            "github": "github",

            # Действия
            "время": "время",
            "дата": "дата",
            "погода": "погода",
            "который час": "который час",
            "интернет": "интернет",
        }

    def enhance(self, text: str) -> str:
        """Улучшение распознанного текста."""
        if not text:
            return text

        # Приведение к нижнему регистру
        text = text.lower().strip()

        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text)

        # Исправление частых ошибок
        for wrong, correct in self.corrections.items():
            text = text.replace(wrong, correct)

        # Удаление слов-паразитов
        parasites = ["эм", "ээ", "ну", "типа", "короче"]
        for parasite in parasites:
            text = text.replace(parasite, "")

        # Повторная очистка от лишних пробелов после удаления
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def extract_numbers(self, text: str) -> List[int]:
        """Извлечение чисел из текста."""
        numbers = re.findall(r'\d+', text)
        return [int(n) for n in numbers]

    def extract_time(self, text: str) -> Dict:
        """Извлечение времени из текста."""
        # Паттерн для времени HH:MM
        time_pattern = r'(\d{1,2}):(\d{2})'
        match = re.search(time_pattern, text)

        if match:
            return {
                "hour": int(match.group(1)),
                "minute": int(match.group(2))
            }

        # Паттерн для "через N минут/часов"
        relative_pattern = r'через\s+(\d+)\s+(минут|час|секунд)'
        match = re.search(relative_pattern, text)

        if match:
            value = int(match.group(1))
            unit = match.group(2)
            return {
                "value": value,
                "unit": unit,
                "relative": True
            }

        return {}

    def extract_date(self, text: str) -> Dict:
        """Извлечение даты из текста."""
        # Паттерн для даты DD.MM.YYYY
        date_pattern = r'(\d{1,2})[.\-\/](\d{1,2})[.\-\/](\d{4})'
        match = re.search(date_pattern, text)

        if match:
            return {
                "day": int(match.group(1)),
                "month": int(match.group(2)),
                "year": int(match.group(3))
            }

        # Относительные даты
        if "завтра" in text:
            return {"relative": "tomorrow"}
        elif "вчера" in text:
            return {"relative": "yesterday"}
        elif "сегодня" in text:
            return {"relative": "today"}

        return {}

    def normalize_command(self, text: str) -> str:
        """Нормализация команд для обработки."""
        text = self.enhance(text)

        # Удаление wake word если есть
        wake_words = ["джарвис", "jarvis"]
        for wake in wake_words:
            if text.startswith(wake):
                text = text[len(wake):].strip()
                break

        return text
