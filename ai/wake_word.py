"""
JARVIS Wake Word Module
Обнаружение голосовой команды активации
"""

import numpy as np
import threading
import queue
import time

try:
    import sounddevice as sd
except (ImportError, OSError):
    sd = None

class WakeWordDetector:
    """Детектор голосовой команды активации"""

    def __init__(self, wake_word: str = "привет джарвис", sensitivity: float = 0.5):
        self.wake_word = wake_word.lower()
        self.sensitivity = sensitivity
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.callback = None

        if sd is None:
            print("⚠️ sounddevice недоступен (требуется PortAudio). Wake word детектор отключён.")
            self.use_openwakeword = False
            return

        try:
            from openwakeword.model import Model
            self.model = Model(wakeword_models=["hey_jarvis_v0.1"])
            self.use_openwakeword = True
        except ImportError:
            self.use_openwakeword = False
            print("⚠️ openwakeword не установлен, используется fallback")

    def start_listening(self, callback=None):
        """Начало прослушивания"""
        self.callback = callback
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print(f"🎤 Слушаю wake word: '{self.wake_word}'")

    def stop_listening(self):
        """Остановка прослушивания"""
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=2)
        print("🔇 Остановлено прослушивание")

    def _listen_loop(self):
        """Основной цикл прослушивания"""
        while self.is_listening:
            try:
                audio_data = sd.rec(
                    frames=self.chunk_size,
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='int16'
                )
                sd.wait()

                if self.use_openwakeword:
                    prediction = self.model.predict(audio_data)
                    for model_name, score in prediction.items():
                        if score > self.sensitivity:
                            print(f"✅ Wake word detected: {model_name}")
                            if self.callback:
                                self.callback()
                            time.sleep(2)
                            break
                else:
                    energy = np.abs(audio_data).mean()
                    if energy > 1000:
                        if self.callback:
                            self.callback()
                        time.sleep(2)

            except Exception as e:
                print(f"❌ Ошибка прослушивания: {e}")
                time.sleep(1)

    def set_sensitivity(self, sensitivity: float):
        """Установка чувствительности"""
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        print(f"🎚️ Чувствительность: {self.sensitivity:.2f}")
