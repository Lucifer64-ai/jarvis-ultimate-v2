"""
JARVIS Streaming TTS Module
Потоковый синтез речи с началом воспроизведения до завершения генерации
"""

import requests
import json
import io
import threading
import queue
import time
from typing import Optional, Callable

class StreamingTTS:
    """Потоковый синтез речи"""

    def __init__(self, api_key: str, voice: str = "nova"):
        self.api_key = api_key
        self.voice = voice
        self.api_url = "https://api.openai.com/v1/audio/speech"
        self.audio_queue = queue.Queue()
        self.is_playing = False

    def synthesize_stream(self, text: str, callback: Optional[Callable] = None):
        """
        Потоковый синтез речи

        Args:
            text: Текст для синтеза
            callback: Функция для обработки аудио chunks
        """
        # Разбиваем текст на предложения
        sentences = self._split_sentences(text)

        threads = []
        for sentence in sentences:
            thread = threading.Thread(
                target=self._synthesize_sentence,
                args=(sentence, callback)
            )
            threads.append(thread)
            thread.start()

        # Ждём завершения всех потоков
        for thread in threads:
            thread.join()

    def _split_sentences(self, text: str) -> list:
        """Разбиение текста на предложения"""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _synthesize_sentence(self, sentence: str, callback: Optional[Callable] = None):
        """Синтез одного предложения"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "tts-1",
            "input": sentence,
            "voice": self.voice,
            "response_format": "mp3"
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                stream=True
            )

            if response.status_code == 200:
                audio_data = response.content

                if callback:
                    callback(audio_data)
                else:
                    self.audio_queue.put(audio_data)
            else:
                print(f"❌ Ошибка TTS: {response.status_code}")

        except Exception as e:
            print(f"❌ Ошибка синтеза: {e}")

    def play_audio(self, audio_data: bytes):
        """Воспроизведение аудио"""
        try:
            import pygame
            pygame.mixer.init()

            # Сохраняем в временный файл
            with io.BytesIO(audio_data) as audio_file:
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

        except ImportError:
            print("⚠️ pygame не установлен")
        except Exception as e:
            print(f"❌ Ошибка воспроизведения: {e}")

    def speak(self, text: str):
        """Синтез и воспроизведение речи"""
        def play_callback(audio_data):
            self.play_audio(audio_data)

        self.synthesize_stream(text, callback=play_callback)

    def set_voice(self, voice: str):
        """Установка голоса"""
        available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if voice in available_voices:
            self.voice = voice
            print(f"🎤 Голос установлен: {voice}")
        else:
            print(f"❌ Недоступный голос. Доступные: {', '.join(available_voices)}")

# Пример использования
if __name__ == "__main__":
    tts = StreamingTTS(api_key="your-api-key", voice="nova")

    # Потоковый синтез
    tts.speak("Привет! Я Джарвис, ваш AI-ассистент. Чем могу помочь?")
