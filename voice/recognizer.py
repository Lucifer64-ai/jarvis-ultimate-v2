"""
Распознавание речи для JARVIS
Поддержка: Whisper (OpenAI), Vosk (offline), SpeechRecognition
"""

import os
import io
import json
import threading
import queue
from typing import Dict, Optional, Callable, List
from pathlib import Path


class VoiceRecognizer:
    """Распознавание речи с поддержкой offline и online режимов."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Настройки
        self.config = brain.config
        self.engine = self.config.get("voice.engine", "whisper")  # whisper, vosk, speechrecognition
        self.language = self.config.get("voice.language", "ru-RU")
        self.sample_rate = self.config.get("voice.sample_rate", 16000)
        self.channels = self.config.get("voice.channels", 1)

        # Состояние
        self.is_listening = False
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread: Optional[threading.Thread] = None
        self.recognition_thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_speech_detected: Optional[Callable[[str], None]] = None
        self.on_command_recognized: Optional[Callable[[str, Dict], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None

        # Модели
        self.whisper_model = None
        self.vosk_model = None

        # Инициализация
        self._init_engine()

    def _init_engine(self):
        """Инициализация движка распознавания."""
        try:
            if self.engine == "whisper":
                self._init_whisper()
            elif self.engine == "vosk":
                self._init_vosk()
            elif self.engine == "speechrecognition":
                self._init_speechrecognition()
            else:
                self.logger.warning(f"Неизвестный движок: {self.engine}, использую whisper")
                self._init_whisper()
        except Exception as e:
            self.logger.error(f"Ошибка инициализации движка: {e}")

    def _init_whisper(self):
        """Инициализация Whisper."""
        try:
            import whisper
            model_name = self.config.get("voice.whisper_model", "base")
            self.whisper_model = whisper.load_model(model_name)
            self.logger.info(f"Whisper модель '{model_name}' загружена")
        except ImportError:
            self.logger.warning("Whisper не установлен, использую SpeechRecognition")
            self._init_speechrecognition()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки Whisper: {e}")

    def _init_vosk(self):
        """Инициализация Vosk (offline)."""
        try:
            from vosk import Model
            model_path = self.config.get("voice.vosk_model_path", "models/vosk-model-ru")
            if Path(model_path).exists():
                self.vosk_model = Model(model_path)
                self.logger.info(f"Vosk модель загружена из {model_path}")
            else:
                self.logger.warning(f"Vosk модель не найдена: {model_path}")
                self._init_speechrecognition()
        except ImportError:
            self.logger.warning("Vosk не установлен, использую SpeechRecognition")
            self._init_speechrecognition()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки Vosk: {e}")

    def _init_speechrecognition(self):
        """Инициализация SpeechRecognition."""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.logger.info("SpeechRecognition инициализирован")
        except ImportError:
            self.logger.error("SpeechRecognition не установлен")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации SpeechRecognition: {e}")

    def start_listening(self) -> Dict:
        """Начать прослушивание микрофона."""
        if self.is_listening:
            return {"status": "ok", "message": "Уже слушаю"}

        try:
            self.is_listening = True
            self.recording_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.recording_thread.start()
            self.logger.info("Начато прослушивание микрофона")
            return {"status": "ok", "message": "Слушаю..."}
        except Exception as e:
            self.is_listening = False
            self.logger.error(f"Ошибка запуска прослушивания: {e}")
            return {"status": "error", "message": str(e)}

    def stop_listening(self) -> Dict:
        """Остановить прослушивание."""
        self.is_listening = False
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        self.logger.info("Прослушивание остановлено")
        return {"status": "ok", "message": "Слушаю остановлено"}

    def _listen_loop(self):
        """Цикл прослушивания микрофона."""
        try:
            import speech_recognition as sr

            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                while self.is_listening:
                    try:
                        audio = self.recognizer.listen(source, timeout=1.0, phrase_time_limit=10.0)

                        # Обработка в отдельном потоке
                        self.recognition_thread = threading.Thread(
                            target=self._process_audio,
                            args=(audio,),
                            daemon=True
                        )
                        self.recognition_thread.start()

                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        if self.on_error:
                            self.on_error(e)
                        continue

        except Exception as e:
            self.logger.error(f"Ошибка в цикле прослушивания: {e}")
            self.is_listening = False

    def _process_audio(self, audio):
        """Обработка аудио и распознавание речи."""
        try:
            text = self._recognize(audio)

            if text and text.strip():
                self.logger.info(f"Распознано: {text}")

                if self.on_speech_detected:
                    self.on_speech_detected(text)

                # Обработка команды
                if self.on_command_recognized:
                    result = self.brain.process_command(text)
                    self.on_command_recognized(text, result)

        except Exception as e:
            self.logger.error(f"Ошибка обработки аудио: {e}")
            if self.on_error:
                self.on_error(e)

    def _recognize(self, audio) -> Optional[str]:
        """Распознавание речи из аудио."""
        if self.engine == "whisper" and self.whisper_model:
            return self._recognize_whisper(audio)
        elif self.engine == "vosk" and self.vosk_model:
            return self._recognize_vosk(audio)
        else:
            return self._recognize_speechrecognition(audio)

    def _recognize_whisper(self, audio) -> Optional[str]:
        """Распознавание через Whisper."""
        try:
            import numpy as np
            import io
            import wave

            # Конвертация аудио в формат для Whisper
            audio_data = audio.get_wav_data(convert_rate=16000, convert_width=2)
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            result = self.whisper_model.transcribe(audio_array, language="ru")
            return result.get("text", "").strip()
        except Exception as e:
            self.logger.error(f"Ошибка Whisper: {e}")
            return None

    def _recognize_vosk(self, audio) -> Optional[str]:
        """Распознавание через Vosk."""
        try:
            from vosk import KaldiRecognizer
            import json

            rec = KaldiRecognizer(self.vosk_model, self.sample_rate)
            audio_data = audio.get_wav_data(convert_rate=self.sample_rate)

            if rec.AcceptWaveform(audio_data):
                result = json.loads(rec.Result())
                return result.get("text", "").strip()
            return None
        except Exception as e:
            self.logger.error(f"Ошибка Vosk: {e}")
            return None

    def _recognize_speechrecognition(self, audio) -> Optional[str]:
        """Распознавание через SpeechRecognition."""
        try:
            # Пробуем Google (online)
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text.strip()
        except Exception as e:
            self.logger.debug(f"Google распознавание не удалось: {e}")

            # Пробуем Sphinx (offline)
            try:
                text = self.recognizer.recognize_sphinx(audio, language=self.language)
                return text.strip()
            except Exception as e2:
                self.logger.error(f"Ошибка распознавания: {e2}")
                return None

    def recognize_from_file(self, file_path: str) -> Dict:
        """Распознавание речи из файла."""
        try:
            import speech_recognition as sr

            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
                text = self._recognize(audio)

                if text:
                    return {"status": "ok", "text": text}
                return {"status": "error", "message": "Не удалось распознать речь"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict:
        """Получить статус распознавателя."""
        return {
            "status": "ok",
            "engine": self.engine,
            "language": self.language,
            "is_listening": self.is_listening,
            "whisper_loaded": self.whisper_model is not None,
            "vosk_loaded": self.vosk_model is not None,
        }

    def set_engine(self, engine: str) -> Dict:
        """Сменить движок распознавания."""
        if engine not in ["whisper", "vosk", "speechrecognition"]:
            return {"status": "error", "message": f"Неизвестный движок: {engine}"}

        self.engine = engine
        self._init_engine()
        return {"status": "ok", "message": f"Движок изменён на {engine}"}

    def set_language(self, language: str) -> Dict:
        """Сменить язык распознавания."""
        self.language = language
        return {"status": "ok", "message": f"Язык изменён на {language}"}
