"""
Модуль голосовой индивидуальности JARVIS (стиль Железного Человека)
- Обращение "Сэр" (Sir)
- Английский мужской голос с британским акцентом
- Эмоциональная интонация (вежливость, ирония, срочность)
"""

from typing import Optional, Dict, List
import logging
import random

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    PYTTSX3_AVAILABLE = False


class VoicePersonality:
    """Индивидуальность голоса JARVIS в стиле J.A.R.V.I.S из Железного Человека."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Конфигурация личности
        personality_config = brain.config.get("voice_personality", {})
        self.address_as_sir = personality_config.get("address_as_sir", True)
        self.sir_name = personality_config.get("sir_name", "Сэр")
        self.british_accent = personality_config.get("british_accent", True)
        self.formality_level = personality_config.get("formality_level", "high")  # high, medium, low
        self.sarcasm_enabled = personality_config.get("sarcasm_enabled", False)

        # Эмоциональные состояния
        self.mood = "professional"  # professional, sarcastic, urgent, helpful, formal
        self.mood_config = {
            "professional": {"rate": 170, "volume": 1.0, "prefix": ""},
            "sarcastic": {"rate": 185, "volume": 0.9, "prefix": "О, конечно, "},
            "urgent": {"rate": 200, "volume": 1.0, "prefix": "Внимание! "},
            "helpful": {"rate": 160, "volume": 1.0, "prefix": "Разрешите помочь, "},
            "formal": {"rate": 165, "volume": 0.95, "prefix": ""},
        }

        # Движок TTS
        self.engine = None
        self._init_tts()

    def _init_tts(self):
        """Инициализация TTS с английским мужским голосом."""
        if not PYTTSX3_AVAILABLE:
            self.logger.warning("pyttsx3 не установлен. Голосовая индивидуальность недоступна.")
            return

        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')

            # Поиск английского мужского голоса (британский акцент)
            selected_voice = None
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower()
                # Приоритет: английский мужской голос
                if ('english' in voice_name or 'en_' in voice_id) and 'male' in voice_name:
                    selected_voice = voice.id
                    break
                # Запасной вариант: любой английский голос
                if selected_voice is None and ('english' in voice_name or 'en_' in voice_id):
                    selected_voice = voice.id

            if selected_voice:
                self.engine.setProperty('voice', selected_voice)
                self.logger.info(f"Голос установлен: {selected_voice}")
            else:
                self.logger.warning("Английский мужской голос не найден, используется системный по умолчанию")

            # Настройка скорости и громкости
            voice_config = self.brain.config.get("voice", {})
            self.engine.setProperty('rate', voice_config.get("rate", 170))
            self.engine.setProperty('volume', voice_config.get("volume", 1.0))

        except Exception as e:
            self.logger.error(f"Ошибка инициализации TTS individualности: {e}")
            self.engine = None

    def speak(self, text: str, mood: Optional[str] = None, force_sir: bool = True) -> None:
        """Произнести текст с индивидуальностью JARVIS."""
        if self.engine is None:
            self.logger.warning("TTS движок недоступен")
            return

        try:
            # Определяем настроение
            current_mood = mood or self.mood
            mood_settings = self.mood_config.get(current_mood, self.mood_config["professional"])

            # Формируем текст с учетом индивидуальности
            spoken_text = self._format_text(text, current_mood, force_sir)

            # Применяем настройки настроения
            self.engine.setProperty('rate', mood_settings["rate"])
            self.engine.setProperty('volume', mood_settings["volume"])

            self.brain.logger.info(f"JARVIS говорит [{current_mood}]: {spoken_text}")
            self.engine.say(spoken_text)
            self.engine.runAndWait()

        except Exception as e:
            self.brain.logger.error(f"Ошибка синтеза речи с индивидуальностью: {e}")

    def _format_text(self, text: str, mood: str, force_sir: bool) -> str:
        """Форматирование текста с учетом индивидуальности."""
        result = text

        # Добавляем префикс настроения
        prefix = self.mood_config[mood]["prefix"]
        if prefix:
            result = prefix + result

        # Обращение "Сэр"
        if self.address_as_sir and force_sir and self.sir_name:
            # Если текст уже начинается с обращения, не дублируем
            greetings = ["сэр", "sir", "привет", "здравствуй", "добрый"]
            starts_with_greeting = any(result.strip().lower().startswith(g) for g in greetings)
            if not starts_with_greeting:
                result = f"{self.sir_name}, {result[0].lower() + result[1:] if result else result}"

        # Элементы иронии (если включены)
        if self.sarcasm_enabled and mood == "sarcastic":
            sarcastic_endings = [
                ", как обычно.",
                ", чего вы вообще ожидали?",
                ", удивительно, не так ли?",
            ]
            if not result.endswith((".", "!", "?")):
                result += random.choice(sarcastic_endings)

        return result

    def set_mood(self, mood: str) -> Dict:
        """Установить эмоциональное состояние."""
        valid_moods = list(self.mood_config.keys())
        if mood not in valid_moods:
            return {"status": "error", "message": f"Недопустимое настроение. Доступны: {', '.join(valid_moods)}"}
        self.mood = mood
        self.logger.info(f"Настроение JARVIS изменено на: {mood}")
        return {"status": "ok", "message": f"Настроение: {mood}"}

    def get_mood(self) -> str:
        """Получить текущее настроение."""
        return self.mood

    def set_sir_name(self, name: str) -> None:
        """Установить имя обращения."""
        self.sir_name = name

    def toggle_sir(self, enabled: bool) -> None:
        """Включить/выключить обращение 'Сэр'."""
        self.address_as_sir = enabled

    def toggle_sarcasm(self, enabled: bool) -> None:
        """Включить/выключить иронию."""
        self.sarcasm_enabled = enabled

    def speak_urgent(self, text: str) -> None:
        """Срочное сообщение."""
        self.speak(text, mood="urgent", force_sir=True)

    def speak_professional(self, text: str) -> None:
        """Профессиональное сообщение."""
        self.speak(text, mood="professional", force_sir=True)

    def speak_formal(self, text: str) -> None:
        """Формальное сообщение."""
        self.speak(text, mood="formal", force_sir=True)

    def speak_helpful(self, text: str) -> None:
        """Помогающее сообщение."""
        self.speak(text, mood="helpful", force_sir=True)

    def get_status(self) -> Dict:
        """Получить статус модуля индивидуальности."""
        return {
            "status": "ok",
            "tts_available": PYTTSX3_AVAILABLE and self.engine is not None,
            "address_as_sir": self.address_as_sir,
            "sir_name": self.sir_name,
            "british_accent": self.british_accent,
            "mood": self.mood,
            "sarcasm_enabled": self.sarcasm_enabled,
            "formality_level": self.formality_level,
        }
