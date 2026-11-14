"""
Hardware Manager - Главный менеджер аппаратного обеспечения JARVIS
"""

from typing import Dict, Optional
import logging


class HardwareManager:
    """Централизованное управление всем железом JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Компоненты
        self.display = None
        self.servos = None
        self.leds = None
        self.sensors = None

        self.initialized = False

    def initialize(self) -> Dict:
        """Инициализация всех аппаратных компонентов."""
        try:
            # Голографический дисплей
            from hardware.holographic_display import HolographicDisplay
            self.display = HolographicDisplay(self.brain)
            self.logger.info("✓ Голографический дисплей загружен")

            # Сервоприводы
            from hardware.servo_controller import ServoController
            self.servos = ServoController(self.brain)
            self.servos.initialize()
            self.logger.info("✓ Сервоприводы загружены")

            # LED индикаторы
            from hardware.led_controller import LEDController
            self.leds = LEDController(self.brain)
            self.leds.initialize()
            self.logger.info("✓ LED индикаторы загружены")

            # Датчики
            from hardware.sensor_manager import SensorManager
            self.sensors = SensorManager(self.brain)
            self.sensors.initialize()
            self.logger.info("✓ Датчики загружены")

            self.initialized = True

            # Начальное состояние
            self.leds.idle()
            self.servos.center()

            return {"status": "ok", "message": "Аппаратное обеспечение инициализировано"}

        except Exception as e:
            self.logger.error(f"Ошибка инициализации hardware: {e}")
            return {"status": "error", "message": str(e)}

    def activate(self) -> Dict:
        """Активировать JARVIS (включение дисплея, приветствие)."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware не инициализирован"}

        try:
            # Включение дисплея
            self.display.activate()

            # Приветственная анимация
            self.leds.pulse((0, 200, 255), duration=2.0)
            self.servos.look_at("center")

            # Показ голограммы
            self.display.show_hologram("default")

            return {"status": "ok", "message": "JARVIS активирован"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def deactivate(self) -> Dict:
        """Деактивировать JARVIS."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware не инициализирован"}

        try:
            self.display.deactivate()
            self.leds.off()
            self.servos.center()

            return {"status": "ok", "message": "JARVIS деактивирован"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def on_listening(self) -> Dict:
        """JARVIS слушает команд."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware не инициализирован"}

        self.leds.listening()
        self.servos.look_at("center")

        return {"status": "ok", "message": "Слушаю..."}

    def on_thinking(self) -> Dict:
        """JARVIS думает."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware не инициализирован"}

        self.leds.thinking()

        return {"status": "ok", "message": "Думаю..."}

    def on_speaking(self) -> Dict:
        """JARVIS говорит."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware не инициализирован"}

        self.leds.speaking()

        return {"status": "ok", "message": "Говорю..."}

    def on_error(self) -> Dict:
        """Ошибка."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware не инициализирован"}

        self.leds.error()
        self.servos.shake()

        return {"status": "ok", "message": "Ошибка"}

    def on_success(self) -> Dict:
        """Успех."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware не инициализирован"}

        self.leds.success()
        self.servos.nod()

        return {"status": "ok", "message": "Успешно"}

    def track_speaker(self, x: int, y: int) -> Dict:
        """Следить за говорящим."""
        if not self.initialized or not self.servos:
            return {"status": "error", "message": "Сервоприводы не готовы"}

        return self.servos.track_speaker(x, y)

    def get_environment(self) -> Dict:
        """Получить данные об окружающей среде."""
        if not self.initialized or not self.sensors:
            return {"status": "error", "message": "Датчики не готовы"}

        return self.sensors.get_all_readings()

    def is_someone_present(self) -> bool:
        """Проверить присутствие человека."""
        if not self.initialized or not self.sensors:
            return False

        return self.sensors.is_someone_present()

    def get_status(self) -> Dict:
        """Полный статус hardware."""
        status = {
            "initialized": self.initialized,
            "components": {}
        }

        if self.display:
            status["components"]["display"] = self.display.get_status()

        if self.servos:
            pan, tilt = self.servos.get_position()
            status["components"]["servos"] = {
                "initialized": self.servos.initialized,
                "position": {"pan": pan, "tilt": tilt}
            }

        if self.leds:
            status["components"]["leds"] = self.leds.get_status()

        if self.sensors:
            status["components"]["sensors"] = {
                "initialized": self.sensors.initialized,
                "readings": self.sensors.get_all_readings()
            }

        return status

    def cleanup(self):
        """Очистка ресурсов."""
        if self.initialized:
            if self.servos:
                self.servos.cleanup()
            if self.leds:
                self.leds.cleanup()
            if self.sensors:
                self.sensors.cleanup()

            self.initialized = False
            self.logger.info("Hardware очищен")
