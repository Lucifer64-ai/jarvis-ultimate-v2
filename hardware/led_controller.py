"""
LED Controller - £¿°в»µ½иµ LED и½´иº°¾°¼и
"""

import time
import threading
from typing import Dict, Optional, Tuple
import logging


class LEDController:
    """£¿°в»µ½иµ LED и½´иº°¾°¼и JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        
        # и½ LED (´» Raspberry Pi GPIO)
        self.led_pins = brain.config.get("hardware.led_pins", [18, 23, 24])  # RGB
        
        # ¡¾¾½и
        self.current_color = (0, 0, 0)
        self.brightness = 100
        self.animation_thread: Optional[threading.Thread] = None
        self.stop_animation = False
        
        self.initialized = False

    def initialize(self) -> Dict:
        """½ии°»и·°и LED."""
        try:
            #  µ°»½¾¹ µ°»и·°ии:
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # for pin in self.led_pins:
            #     GPIO.setup(pin, GPIO.OUT)
            #     self.pwm.append(GPIO.PWM(pin, 1000))
            #     self.pwm[-1].start(0)
            
            self.initialized = True
            self.logger.info("LED и½´иº°¾ и½ии°»и·и¾в°½")
            return {"status": "ok", "message": "LED ³¾¾в º °±¾µ"}
        except Exception as e:
            self.logger.error(f"агента и½ии°»и·°ии LED: {e}")
            return {"status": "error", "message": str(e)}

    def set_color(self, r: int, g: int, b: int) -> Dict:
        """£°½¾вº° вµ° (0-255)."""
        if not self.initialized:
            return {"status": "error", "message": "LED ни и½ии°»и·и¾в°½"}
        
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        self.current_color = (r, g, b)
        
        #  µ°»½¾¹ µ°»и·°ии:
        # duty_r = (r / 255.0) * (self.brightness / 100.0) * 100
        # duty_g = (g / 255.0) * (self.brightness / 100.0) * 100
        # duty_b = (b / 255.0) * (self.brightness / 100.0) * 100
        # self.pwm[0].ChangeDutyCycle(duty_r)
        # self.pwm[1].ChangeDutyCycle(duty_g)
        # self.pwm[2].ChangeDutyCycle(duty_b)
        
        self.logger.info(f"LED вµ: RGB({r}, {g}, {b})")
        return {"status": "ok", "message": f"¦вµ °½¾в»µ½: RGB({r}, {g}, {b})"}

    def set_brightness(self, level: int) -> Dict:
        """£°½¾вº° º¾и (0-100)."""
        self.brightness = max(0, min(100, level))
        r, g, b = self.current_color
        return self.set_color(r, g, b)

    def off(self) -> Dict:
        """º»и LED."""
        self.stop_animation = True
        return self.set_color(0, 0, 0)

    # µ´°½¾в»µ½½µ вµ°
    def idle(self) -> Dict:
        """ µ¶и¼ ¾¶и´°½и - и½и¹."""
        return self.set_color(0, 100, 255)

    def listening(self) -> Dict:
        """¡»°µ - ·µ»µ½¹."""
        return self.set_color(0, 255, 100)

    def speaking(self) -> Dict:
        """¾в¾и - ³¾»±¾¹."""
        return self.set_color(0, 200, 255)

    def thinking(self) -> Dict:
        """¼°µ - ¶µ»¹."""
        return self.set_color(255, 200, 0)

    def error(self) -> Dict:
        """агента - º°½¹."""
        return self.set_color(255, 0, 0)

    def success(self) -> Dict:
        """£¿µ - ·µ»µ½¹."""
        return self.set_color(0, 255, 0)

    # ½и¼°ии
    def pulse(self, color: Tuple[int, int, int], duration: float = 2.0) -> Dict:
        """»°и."""
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
        
        return {"status": "ok", "message": "»°и ·°¿µ½°"}

    def breathe(self, duration: float = 3.0) -> Dict:
        """°½иµ - ¿»°в½° ¿»°и и½и¼."""
        return self.pulse((0, 100, 255), duration)

    def rainbow(self, duration: float = 5.0) -> Dict:
        """ °´³°."""
        self.stop_animation = True
        time.sleep(0.1)
        self.stop_animation = False
        
        def animate():
            colors = [
                (255, 0, 0),    # °½¹
                (255, 127, 0),  # °½¶µв¹
                (255, 255, 0),  # µ»¹
                (0, 255, 0),    # µ»µ½¹
                (0, 0, 255),    # ¡и½и¹
                (75, 0, 130),   # ½´и³¾
                (148, 0, 211)   # ¤и¾»µ¾в¹
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
        """иº° µ¾в."""
        self.stop_animation = True
        if self.initialized:
            #  µ°»½¾¹ µ°»и·°ии:
            # for pwm in self.pwm:
            #     pwm.stop()
            # GPIO.cleanup()
            self.initialized = False
            self.logger.info("LED ¾иµ½")
