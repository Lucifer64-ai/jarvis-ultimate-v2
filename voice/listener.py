"""
Распознавание речи JARVIS
"""

import speech_recognition as sr
from typing import Optional, Dict


class VoiceListener:
    """Распознавание голосовых команд."""

    def __init__(self, brain):
        self.brain = brain
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.wake_word = brain.config.get("voice", {}).get("wake_word", "джарвис")

        # Настройка распознавания
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300

    def listen(self) -> Optional[str]:
        """Слушать и распознать речь."""
        try:
            with self.microphone as source:
                self.brain.logger.info("Слушаю...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

            self.brain.logger.info("Распознаю речь...")
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            self.brain.logger.info(f"Распознано: {text}")
            return text

        except sr.WaitTimeoutError:
            self.brain.logger.debug("Таймаут ожидания речи")
            return None
        except sr.UnknownValueError:
            self.brain.logger.debug("Не удалось распознать речь")
            return None
        except sr.RequestError as e:
            self.brain.logger.error(f"Ошибка сервиса распознавания: {e}")
            return None
        except Exception as e:
            self.brain.logger.error(f"Ошибка распознавания: {e}")
            return None

    def listen_for_wake_word(self) -> bool:
        """Слушать wake word."""
        text = self.listen()
        if text and self.wake_word.lower() in text.lower():
            return True
        return False

    def continuous_listen(self, callback):
        """Непрерывное прослушивание."""
        while True:
            text = self.listen()
            if text:
                callback(text)
