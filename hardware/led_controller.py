"""
LED Controller - Управление LED индикаторами
"""

import time
import threading
from typing import Dict, Optional, Tuple
import logging


class LEDController:
    """Управление LED индикаторами JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Пины LED (для Raspberry Pi GPIO)
        self.led_pins = brain.config.get("hardware.led_pins", [18, 23, 24])  # RGB

        # Состояния
        self.current_color = (0, 0, 0)
        self.brightness = 100
        self.animation_thread: Optional[threading.Thread] = None
        self.stop_animation = False

        self.initialized = False

    def initialize(self) -> Dict:
        """Инициализация LED."""
        try:
            # В реальной реализации:
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # for pin in self.led_pins:
            #     GPIO.setup(pin, GPIO.OUT)
            #     self.pwm.append(GPIO.PWM(pin, 1000))
            #     self.pwm[-1].start(0)

            self.initialized = True
            self.logger.info("LED индикаторы инициализированы")
            return {"status": "ok", "message": "LED готовы к работе"}
        except Exception as e:
            self.logger.error(f"Ошибка инициализации LED: {e}")
            return {"status": "error", "message": str(e)}

    def set_color(self, r: int, g: int, b: int) -> Dict:
        """Установка цвета (0-255)."""
        if not self.initialized:
            return {"status": "error", "message": "LED не инициализированы"}

        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        self.current_color = (r, g, b)

        # В реальной реализации:
        # duty_r = (r / 255.0) * (self.brightness / 100.0) * 100
        # duty_g = (g / 255.0) * (self.brightness / 100.0) * 100
        # duty_b = (b / 255.0) * (self.brightness / 100.0) * 100
        # self.pwm[0].ChangeDutyCycle(duty_r)
        # self.pwm[1].ChangeDutyCycle(duty_g)
        # self.pwm[2].ChangeDutyCycle(duty_b)

        self.logger.info(f"LED цвет: RGB({r}, {g}, {b})")
        return {"status": "ok", "message": f"Цвет установлен: RGB({r}, {g}, {b})"}

    def set_brightness(self, level: int) -> Dict:
        """Установка яркости (0-100)."""
        self.brightness = max(0, min(100, level))
        r, g, b = self.current_color
        return self.set_color(r, g, b)

    def off(self) -> Dict:
        """Выключить LED."""
        self.stop_animation = True
        return self.set_color(0, 0, 0)

    # Анимации
    def idle(self) -> Dict:
        """Режим ожидания - синий."""
        return self.set_color(0, 100, 255)

    def listening(self) -> Dict:
        """Слушает - зелёный."""
        return self.set_color(0, 255, 100)

    def speaking(self) -> Dict:
        """Говорит - голубой."""
        return self.set_color(0, 200, 255)

    def thinking(self) -> Dict:
        """Думает - жёлтый."""
        return self.set_color(255, 200, 0)

    def error(self) -> Dict:
        """Ошибка - красный."""
        return self.set_color(255, 0, 0)

    def success(self) -> Dict:
        """Успех - зелёный."""
        return self.set_color(0, 255, 0)

    # Анимации
    def pulse(self, color: Tuple[int, int, int], duration: float = 2.0) -> Dict:
        """Пульсация."""
        self.stop_animation = True
        time.sleep(0.1)
        self.stop_animation = False

        def animate():
            r, g, b = color
            steps = 50
            for i in range(steps):
                if self.stop_animation:
                    break
                factor = (i / steps) * (self.brightness / 100.0)
                self.set_color(int(r * factor), int(g * factor), int(b * factor))
                time.sleep(duration / steps / 2)

            for i in range(steps, -1, -1):
                if self.stop_animation:
                    break
                factor = (i / steps) * (self.brightness / 100.0)
                self.set_color(int(r * factor), int(g * factor), int(b * factor))
                time.sleep(duration / steps / 2)

        self.animation_thread = threading.Thread(target=animate, daemon=True)
        self.animation_thread.start()

        return {"status": "ok", "message": "Пульсация запущена"}

    def breathe(self, duration: float = 3.0) -> Dict:
        """Дыхание - плавная пульсация текущим цветом."""
        return self.pulse(self.current_color, duration)

    def rainbow(self, duration: float = 5.0) -> Dict:
        """Радуга."""
        self.stop_animation = True
        time.sleep(0.1)
        self.stop_animation = False

        def animate():
            colors = [
                (255, 0, 0),    # Красный
                (255, 127, 0),  # Оранжевый
                (255, 255, 0),  # Жёлтый
                (0, 255, 0),    # Зелёный
                (0, 0, 255),    # Синий
                (75, 0, 130),   # Индиго
                (148, 0, 211),  # Фиолетовый
            ]

            steps_per_color = 20
            total_steps = len(colors) * steps_per_color
            step_duration = duration / total_steps

            for i in range(total_steps):
                if self.stop_animation:
                    break

                color_idx = i // steps_per_color
                step_in_color = i % steps_per_color

                current = colors[color_idx]
                next_color = colors[(color_idx + 1) % len(colors)]

                factor = step_in_color / steps_per_color
                r = int(current[0] * (1 - factor) + next_color[0] * factor)
                g = int(current[1] * (1 - factor) + next_color[1] * factor)
                b = int(current[2] * (1 - factor) + next_color[2] * factor)

                brightness_factor = self.brightness / 100.0
                self.set_color(int(r * brightness_factor), int(g * brightness_factor), int(b * brightness_factor))
                time.sleep(step_duration)

        self.animation_thread = threading.Thread(target=animate, daemon=True)
        self.animation_thread.start()

        return {"status": "ok", "message": "Радуга запущена"}

    def cleanup(self):
        """Очистка ресурсов."""
        self.stop_animation = True
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)

        # В реальной реализации:
        # for pwm in self.pwm:
        #     pwm.stop()
        # GPIO.cleanup()

        self.initialized = False
        self.logger.info("LED ресурсы освобождены")
