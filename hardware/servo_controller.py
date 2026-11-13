"""
Servo Controller - голосовые µ²¾¿¸²¾´°¼¸ для ´²¸¶µ½¸ "³¾»¾²"
"""

import time
from typing import Dict, Optional, Tuple
import logging


class ServoController:
    """голосовые µ²¾¿¸²¾´°¼¸ JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        
        # ¸½ µ²¾¿¸²¾´¾² (для Raspberry Pi GPIO)
        self.pan_pin = brain.config.get("hardware.servo_pan_pin", 17)
        self.tilt_pin = brain.config.get("hardware.servo_tilt_pin", 27)
        
        # ¢µº¸µ ³»
        self.pan_angle = 90  # ¾из¾½°»½¾µ ¿¾»¾¶µ½¸µ (0-180)
        self.tilt_angle = 90  # µ¸º°»½¾µ ¿¾»¾¶µ½¸µ (0-180)
        
        # ³°½¸µ½¸
        self.pan_min = 0
        self.pan_max = 180
        self.tilt_min = 45
        self.tilt_max = 135
        
        self.initialized = False

    def initialize(self) -> Dict:
        """½¸¸°»из°¸ µ²¾¿¸²¾´¾²."""
        try:
            #  µ°»½¾¹ µ°»из°¸¸:
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(self.pan_pin, GPIO.OUT)
            # GPIO.setup(self.tilt_pin, GPIO.OUT)
            # self.pwm_pan = GPIO.PWM(self.pan_pin, 50)
            # self.pwm_tilt = GPIO.PWM(self.tilt_pin, 50)
            # self.pwm_pan.start(7.5)  # ¦µ½°»½¾µ ¿¾»¾¶µ½¸µ
            # self.pwm_tilt.start(7.5)
            
            self.initialized = True
            self.logger.info("¡µ²¾¿¸²¾´ ¸½¸¸°»из¸¾²°½")
            return {"status": "ok", "message": "¡µ²¾¿¸²¾´ ³¾¾² º °±¾µ"}
        except Exception as e:
            self.logger.error(f"агента ¸½¸¸°»из°¸¸ µ²¾¿¸²¾´¾²: {e}")
            return {"status": "error", "message": str(e)}

    def move_to(self, pan: int, tilt: int) -> Dict:
        """µµ¼µµ½¸µ ² º°·°½½ ¿¾·¸¸."""
        if not self.initialized:
            return {"status": "error", "message": "¡µ²¾¿¸²¾´ ни ¸½¸¸°»из¸¾²°½"}
        
        # ³°½¸µ½¸µ ³»¾²
        pan = max(self.pan_min, min(self.pan_max, pan))
        tilt = max(self.tilt_min, min(self.tilt_max, tilt))
        
        try:
            #  µ°»½¾¹ µ°»из°¸¸:
            # duty_pan = 2.5 + (pan / 18.0)
            # duty_tilt = 2.5 + (tilt / 18.0)
            # self.pwm_pan.ChangeDutyCycle(duty_pan)
            # self.pwm_tilt.ChangeDutyCycle(duty_tilt)
            
            self.pan_angle = pan
            self.tilt_angle = tilt
            
            self.logger.info(f"¡µ²¾¿¸²¾´: pan={pan}°, tilt={tilt}°")
            time.sleep(0.5)  # µ¼ на ¿µµ¼µµ½¸µ
            
            return {"status": "ok", "message": f"¾·¸¸: {pan}°, {tilt}°"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def look_at(self, direction: str) -> Dict:
        """¾¼¾µ ² º°·°½½¾¼ на¿°²»µ½¸¸."""
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
        
        return {"status": "error", "message": f"µиз²µ½¾µ на¿°²»µ½¸µ: {direction}"}

    def track_speaker(self, x: int, y: int) -> Dict:
        """¡»µ´¸ ·° ³¾²¾¸¼ (º¾¾´¸на »¸°)."""
        # µ¾±°·¾²°½¸µ º¾¾´¸на º°¼µ ² ³» µ²¾¿¸²¾´¾²
        # µ´¿¾»°³°µ, ¾ º°¼µ° ¸¼µµ ³¾» ¾±·¾° 60°
        
        # ¦µ½ из¾±°¶µ½¸ - µ½ µ²¾¿¸²¾´¾²
        center_x = 320  # » º°¼µ 640x480
        center_y = 240
        
        # ¡¼µµ½¸µ ¾ µ½°
        offset_x = x - center_x
        offset_y = y - center_y
        
        # µ¾±°·¾²°½¸µ ² ³» (¿¸¼µна ¾¼»°)
        pan_offset = (offset_x / center_x) * 45  # ±45°
        tilt_offset = (offset_y / center_y) * 45  # ±45°
        
        new_pan = int(self.pan_angle + pan_offset)
        new_tilt = int(self.tilt_angle - tilt_offset)  # ½²µ¸ для µµ²µ½½¾³¾ ´²¸¶µ½¸
        
        return self.move_to(new_pan, new_tilt)

    def center(self) -> Dict:
        """µ½ ² µ½°»½¾µ ¿¾»¾¶µ½¸µ."""
        return self.look_at("center")

    def nod(self) -> Dict:
        """¸²¾º (´°)."""
        self.move_to(90, 110)
        time.sleep(0.3)
        self.move_to(90, 70)
        time.sleep(0.3)
        self.move_to(90, 90)
        return {"status": "ok", "message": "¸²¾º"}

    def shake(self) -> Dict:
        """¾º°¸²°½¸µ (ни)."""
        self.move_to(70, 90)
        time.sleep(0.3)
        self.move_to(110, 90)
        time.sleep(0.3)
        self.move_to(90, 90)
        return {"status": "ok", "message": "¾º°¸²°½¸µ"}

    def get_position(self) -> Tuple[int, int]:
        """ошибки µº ¿¾·¸¸."""
        return (self.pan_angle, self.tilt_angle)

    def cleanup(self):
        """¸º° µ¾²."""
        if self.initialized:
            #  µ°»½¾¹ µ°»из°¸¸:
            # self.pwm_pan.stop()
            # self.pwm_tilt.stop()
            # GPIO.cleanup()
            self.initialized = False
            self.logger.info("¡µ²¾¿¸²¾´ ¾¸µ½")
