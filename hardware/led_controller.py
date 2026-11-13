"""
LED Controller - £¿°²»µ½¸µ LED ¸½´¸º°¾°¼¸
"""

import time
import threading
from typing import Dict, Optional, Tuple
import logging


class LEDController:
    """£¿°²»µ½¸µ LED ¸½´¸º°¾°¼¸ JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        
        # ¸½ LED (´» Raspberry Pi GPIO)
        self.led_pins = brain.config.get("hardware.led_pins", [18, 23, 24])  # RGB
        
        # ¡¾¾½¸
        self.current_color = (0, 0, 0)
        self.brightness = 100
        self.animation_thread: Optional[threading.Thread] = None
        self.stop_animation = False
        
        self.initialized = False

    def initialize(self) -> Dict:
        """½¸¸°»¸·°¸ LED."""
        try:
            #  µ°»½¾¹ µ°»¸·°¸¸:
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # for pin in self.led_pins:
            #     GPIO.setup(pin, GPIO.OUT)
            #     self.pwm.append(GPIO.PWM(pin, 1000))
            #     self.pwm[-1].start(0)
            
            self.initialized = True
            self.logger.info("LED ¸½´¸º°¾ ¸½¸¸°»¸·¸¾²°½")
            return {"status": "ok", "message": "LED ³¾¾² º °±¾µ"}
        except Exception as e:
            self.logger.error(f"¸±º° ¸½¸¸°»¸·°¸¸ LED: {e}")
            return {"status": "error", "message": str(e)}

    def set_color(self, r: int, g: int, b: int) -> Dict:
        """£°½¾²º° ²µ° (0-255)."""
        if not self.initialized:
            return {"status": "error", "message": "LED ½µ ¸½¸¸°»¸·¸¾²°½"}
        
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        self.current_color = (r, g, b)
        
        #  µ°»½¾¹ µ°»¸·°¸¸:
        # duty_r = (r / 255.0) * (self.brightness / 100.0) * 100
        # duty_g = (g / 255.0) * (self.brightness / 100.0) * 100
        # duty_b = (b / 255.0) * (self.brightness / 100.0) * 100
        # self.pwm[0].ChangeDutyCycle(duty_r)
        # self.pwm[1].ChangeDutyCycle(duty_g)
        # self.pwm[2].ChangeDutyCycle(duty_b)
        
        self.logger.info(f"LED ²µ: RGB({r}, {g}, {b})")
        return {"status": "ok", "message": f"¦²µ °½¾²»µ½: RGB({r}, {g}, {b})"}

    def set_brightness(self, level: int) -> Dict:
        """£°½¾²º° º¾¸ (0-100)."""
        self.brightness = max(0, min(100, level))
        r, g, b = self.current_color
        return self.set_color(r, g, b)

    def off(self) -> Dict:
        """º»¸ LED."""
        self.stop_animation = True
        return self.set_color(0, 0, 0)

    # µ´°½¾²»µ½½µ ²µ°
    def idle(self) -> Dict:
        """ µ¶¸¼ ¾¶¸´°½¸ - ¸½¸¹."""
        return self.set_color(0, 100, 255)

    def listening(self) -> Dict:
        """¡»°µ - ·µ»µ½¹."""
        return self.set_color(0, 255, 100)

    def speaking(self) -> Dict:
        """¾²¾¸ - ³¾»±¾¹."""
        return self.set_color(0, 200, 255)

    def thinking(self) -> Dict:
        """¼°µ - ¶µ»¹."""
        return self.set_color(255, 200, 0)

    def error(self) -> Dict:
        """¸±º° - º°½¹."""
        return self.set_color(255, 0, 0)

    def success(self) -> Dict:
        """£¿µ - ·µ»µ½¹."""
        return self.set_color(0, 255, 0)

    # ½¸¼°¸¸
    def pulse(self, color: Tuple[int, int, int], duration: float = 2.0) -> Dict:
        """»°¸."""
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
        
        return {"status": "ok", "message": "»°¸ ·°¿µ½°"}

    def breathe(self, duration: float = 3.0) -> Dict:
        """°½¸µ - ¿»°²½° ¿»°¸ ¸½¸¼."""
        return self.pulse((0, 100, 255), duration)

    def rainbow(self, duration: float = 5.0) -> Dict:
        """ °´³°."""
        self.stop_animation = True
        time.sleep(0.1)
        self.stop_animation = False
        
        def animate():
            colors = [
                (255, 0, 0),    # °½¹
                (255, 127, 0),  # °½¶µ²¹
                (255, 255, 0),  # µ»¹
                (0, 255, 0),    # µ»µ½¹
                (0, 0, 255),    # ¡¸½¸¹
                (75, 0, 130),   # ½´¸³¾
                (148, 0, 211)   # ¤¸¾»µ¾²¹
            ]
            
            step_time = duration / len(colors)
            for color in colors:
                if self.stop_animation:
                    break
                r, g, b = color
                factor = self.brightness / 100.0
                self.set_color(int(r * factor), int(g * factor), int(b * factor))
                time.sleep(step_time)
        
        self.animation_thread = threading.Thread(target=animate, daemon=True)
        self.animation_thread.start()
        
        return {"status": "ok", "message": " °´³° ·°¿µ½°"}

    def get_status(self) -> Dict:
        """¡° LED."""
        return {
            "initialized": self.initialized,
            "color": self.current_color,
            "brightness": self.brightness
        }

    def cleanup(self):
        """¸º° µ¾²."""
        self.stop_animation = True
        if self.initialized:
            #  µ°»½¾¹ µ°»¸·°¸¸:
            # for pwm in self.pwm:
            #     pwm.stop()
            # GPIO.cleanup()
            self.initialized = False
            self.logger.info("LED ¾¸µ½")
