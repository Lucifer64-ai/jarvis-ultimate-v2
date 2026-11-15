"""
Wake Word Сервис - фоновое распознавание "Джарвис"
"""

import threading
import queue
import time
from typing import Dict, Optional, Callable
import logging


class WakeWordService:
    """Сервис фонового распознавания wake word."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.wake_word = brain.config.get("voice.wake_word", "джарвис")
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None

    def start(self, callback: Callable = None) -> Dict:
        """Запуск сервиса."""
        if self.running:
            return {"status": "error", "message": "Сервис уже запущен"}

        self.callback = callback
        self.running = True

        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

        self.logger.info(f"Wake word сервис запущен. Слушаю '{self.wake_word}'")
        return {"status": "ok", "message": f"Слушаю '{self.wake_word}'"}

    def stop(self) -> Dict:
        """Остановка сервиса."""
        if not self.running:
            return {"status": "error", "message": "Сервис не запущен"}

        self.running = False

        if self.thread:
            self.thread.join(timeout=2)

        self.logger.info("Wake word сервис остановлен")
        return {"status": "ok", "message": "Сервис остановлен"}

    def _listen_loop(self):
        """Цикл распознавания."""
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            microphone = sr.Microphone()

            self.logger.info("Wake word: микрофон инициализирован")

            while self.running:
                try:
                    with microphone as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=2)

                    # Распознавание
                    try:
                        text = recognizer.recognize_google(audio, language="ru-RU")
                        text_lower = text.lower().strip()

                        # Проверка wake word
                        if self.wake_word in text_lower:
                            self.logger.info(f"Wake word обнаружен: {text}")

                            if self.callback:
                                self.callback(text)

                    except sr.UnknownValueError:
                        pass  # Не распознано
                    except sr.RequestError as e:
                        self.logger.error(f"Ошибка распознавания: {e}")

                except Exception as e:
                    # Таймаут или другая ошибка - продолжаем
                    pass

                time.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Ошибка wake word сервиса: {e}")

    def is_running(self) -> bool:
        """Проверить, запущен ли сервис."""
        return self.running

    def set_wake_word(self, wake_word: str) -> Dict:
        """Установить wake word."""
        self.wake_word = wake_word.lower().strip()
        # Config.update() сохраняет значение в config.json
        if hasattr(self.brain.config, "update"):
            self.brain.config.update("voice.wake_word", self.wake_word)
        self.logger.info(f"Wake word изменён: {self.wake_word}")
        return {"status": "ok", "message": f"Wake word: {self.wake_word}"}
