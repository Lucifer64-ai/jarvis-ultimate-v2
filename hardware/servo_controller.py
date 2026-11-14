"""
Servo Controller - Управление сервоприводами для движения "головы"
"""

import time
from typing import Dict, Optional, Tuple
import logging


class ServoController:
    """Управление сервоприводами JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Пины сервоприводов (для Raspberry Pi GPIO)
        self.pan_pin = brain.config.get("hardware.servo_pan_pin", 17)
        self.tilt_pin = brain.config.get("hardware.servo_tilt_pin", 27)

        # Текущие углы
        self.pan_angle = 90  # Горизонтальное положение (0-180)
        self.tilt_angle = 90  # Вертикальное положение (0-180)

        # Ограничения
        self.pan_min = 0
        self.pan_max = 180
        self.tilt_min = 45
        self.tilt_max = 135

        self.initialized = False

    def initialize(self) -> Dict:
        """Инициализация сервоприводов."""
        try:
            # В реальной реализации:
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(self.pan_pin, GPIO.OUT)
            # GPIO.setup(self.tilt_pin, GPIO.OUT)
            # self.pwm_pan = GPIO.PWM(self.pan_pin, 50)
            # self.pwm_tilt = GPIO.PWM(self.tilt_pin, 50)
            # self.pwm_pan.start(7.5)  # Центральное положение
            # self.pwm_tilt.start(7.5)

            self.initialized = True
            self.logger.info("Сервоприводы инициализированы")
            return {"status": "ok", "message": "Сервоприводы готовы к работе"}
        except Exception as e:
            self.logger.error(f"Ошибка инициализации сервоприводов: {e}")
            return {"status": "error", "message": str(e)}

    def move_to(self, pan: int, tilt: int) -> Dict:
        """Перемещение в указанную позицию."""
        if not self.initialized:
            return {"status": "error", "message": "Сервопривод не инициализирован"}

        # Ограничение углов
        pan = max(self.pan_min, min(self.pan_max, pan))
        tilt = max(self.tilt_min, min(self.tilt_max, tilt))

        try:
            # В реальной реализации:
            # duty_pan = 2.5 + (pan / 18.0)
            # duty_tilt = 2.5 + (tilt / 18.0)
            # self.pwm_pan.ChangeDutyCycle(duty_pan)
            # self.pwm_tilt.ChangeDutyCycle(duty_tilt)

            self.pan_angle = pan
            self.tilt_angle = tilt

            self.logger.info(f"Сервопривод: pan={pan}°, tilt={tilt}°")
            time.sleep(0.5)  # Время на перемещение

            return {"status": "ok", "message": f"Позиция: {pan}°, {tilt}°"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def look_at(self, direction: str) -> Dict:
        """Посмотреть в указанном направлении."""
        directions = {
            "center": (90, 90),
            "left": (45, 90),
            "right": (135, 90),
            "up": (90, 135),
            "down": (90, 45),
            "up-left": (45, 135),
            "up-right": (135, 135),
            "down-left": (45, 45),
            "down-right": (135, 45)
        }

        if direction in directions:
            pan, tilt = directions[direction]
            return self.move_to(pan, tilt)

        return {"status": "error", "message": f"Неизвестное направление: {direction}"}

    def track_speaker(self, x: int, y: int) -> Dict:
        """Следить за говорящим (координаты лица)."""
        # Преобразование координат камеры в углы сервоприводов
        # Предполагается, что камера имеет угол обзора 60°

        # Центр изображения - центр сервоприводов
        center_x = 320  # Для камеры 640x480
        center_y = 240

        # Смещение от центра
        offset_x = x - center_x
        offset_y = y - center_y

        # Преобразование в углы (примерное соотношение)
        pan_offset = (offset_x / center_x) * 45  # ±45°
        tilt_offset = (offset_y / center_y) * 45  # ±45°

        new_pan = int(self.pan_angle + pan_offset)
        new_tilt = int(self.tilt_angle - tilt_offset)  # Инверсия для естественного движения

        return self.move_to(new_pan, new_tilt)

    def center(self) -> Dict:
        """Вернуться в центральное положение."""
        return self.look_at("center")

    def nod(self) -> Dict:
        """Кивок (да)."""
        self.move_to(90, 110)
        time.sleep(0.3)
        self.move_to(90, 70)
        time.sleep(0.3)
        self.move_to(90, 90)
        return {"status": "ok", "message": "Кивок"}

    def shake(self) -> Dict:
        """Покачивание (нет)."""
        self.move_to(70, 90)
        time.sleep(0.3)
        self.move_to(110, 90)
        time.sleep(0.3)
        self.move_to(90, 90)
        return {"status": "ok", "message": "Покачивание"}

    def get_position(self) -> Tuple[int, int]:
        """Получить текущие позиции."""
        return (self.pan_angle, self.tilt_angle)

    def cleanup(self):
        """Очистка ресурсов."""
        if self.initialized:
            # В реальной реализации:
            # self.pwm_pan.stop()
            # self.pwm_tilt.stop()
            # GPIO.cleanup()
            self.initialized = False
            self.logger.info("Сервопривод очищены")
