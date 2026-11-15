"""
Синтез речи JARVIS
"""

from typing import Optional

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class VoiceSpeaker:
    """Синтез речи."""

    def __init__(self, brain):
        self.brain = brain
        if pyttsx3 is None:
            raise ImportError("pyttsx3 не установлен. Установите: pip install pyttsx3")

        self.engine = pyttsx3.init()

        # Настройка голоса
        voice_config = brain.config.get("voice", {})
        self.engine.setProperty('rate', voice_config.get("rate", 180))
        self.engine.setProperty('volume', voice_config.get("volume", 1.0))

        # Выбор русского голоса
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'russian' in voice.name.lower() or 'ru' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text: str):
        """Произнести текст."""
        try:
            self.brain.logger.info(f"Говорю: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.brain.logger.error(f"Ошибка синтеза речи: {e}")

    def set_rate(self, rate: int):
        """Установить скорость речи."""
        self.engine.setProperty('rate', rate)

    def set_volume(self, volume: float):
        """Установить громкость."""
        self.engine.setProperty('volume', volume)
