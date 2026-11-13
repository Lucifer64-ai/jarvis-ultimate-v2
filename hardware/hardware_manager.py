"""
Hardware Manager - »°²½¹ ¼µни´¶µ °¿¿°°½¾³¾ ¾±µ¿µµ½¸ JARVIS
"""

from typing import Dict, Optional
import logging


class HardwareManager:
    """¦µ½°»из¾²°½½¾µ ¿°²»µ½¸µ ²µ¼ ¶µ»µ·¾¼ JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        
        # ¾¼¿¾ни½
        self.display = None
        self.servos = None
        self.leds = None
        self.sensors = None
        
        self.initialized = False

    def initialize(self) -> Dict:
        """½¸¸°»из°¸ ²µ °¿¿°°½ º¾¼¿¾ни½¾²."""
        try:
            # ¾»¾³°¸µº¸¹ ´¸¿»µ¹
            from hardware.holographic_display import HolographicDisplay
            self.display = HolographicDisplay(self.brain)
            self.logger.info("¢ ¾»¾³°¸µº¸¹ ´¸¿»µ¹ ·°³¶µ½")
            
            # ¡µ²¾¿¸²¾´
            from hardware.servo_controller import ServoController
            self.servos = ServoController(self.brain)
            self.servos.initialize()
            self.logger.info("¢ ¡µ²¾¿¸²¾´ ·°³¶µ½")
            
            # LED ¸½´¸º°¾
            from hardware.led_controller import LEDController
            self.leds = LEDController(self.brain)
            self.leds.initialize()
            self.logger.info("¢ LED ¸½´¸º°¾ ·°³¶µ½")
            
            # °¸º¸
            from hardware.sensor_manager import SensorManager
            self.sensors = SensorManager(self.brain)
            self.sensors.initialize()
            self.logger.info("¢ °¸º¸ ·°³¶µ½")
            
            self.initialized = True
            
            # °°»½¾µ ¾¾½¸µ
            self.leds.idle()
            self.servos.center()
            
            return {"status": "ok", "message": "¿¿°°½¾µ ¾±µ¿µµ½¸µ ¸½¸¸°»из¸¾²°½¾"}
        
        except Exception as e:
            self.logger.error(f"агента ¸½¸¸°»из°¸¸ hardware: {e}")
            return {"status": "error", "message": str(e)}

    def activate(self) -> Dict:
        """º¸²°¸ JARVIS (²º»µ½¸µ ´¸¿»µ, ¿¸²µ²¸µ)."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware ни ¸½¸¸°»из¸¾²°½"}
        
        try:
            # º»µ½¸µ ´¸¿»µ
            self.display.activate()
            
            # ¸²µ²µ½на °½¸¼°¸
            self.leds.pulse((0, 200, 255), duration=2.0)
            self.servos.look_at("center")
            
            # ¾º°· ³¾»¾³°¼¼
            self.display.show_hologram("default")
            
            return {"status": "ok", "message": "JARVIS °º¸²¸¾²°½"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def deactivate(self) -> Dict:
        """µ°º¸²°¸ JARVIS."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware ни ¸½¸¸°»из¸¾²°½"}
        
        try:
            self.display.deactivate()
            self.leds.off()
            self.servos.center()
            
            return {"status": "ok", "message": "JARVIS ´µ°º¸²¸¾²°½"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def on_listening(self) -> Dict:
        """JARVIS »°µ команд."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware ни ¸½¸¸°»из¸¾²°½"}
        
        self.leds.listening()
        self.servos.look_at("center")
        
        return {"status": "ok", "message": "¡»°..."}

    def on_thinking(self) -> Dict:
        """JARVIS ´¼°µ."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware ни ¸½¸¸°»из¸¾²°½"}
        
        self.leds.thinking()
        
        return {"status": "ok", "message": "¼°..."}

    def on_speaking(self) -> Dict:
        """JARVIS ³¾²¾¸."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware ни ¸½¸¸°»из¸¾²°½"}
        
        self.leds.speaking()
        
        return {"status": "ok", "message": "¾²¾..."}

    def on_error(self) -> Dict:
        """агента."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware ни ¸½¸¸°»из¸¾²°½"}
        
        self.leds.error()
        self.servos.shake()
        
        return {"status": "ok", "message": "агента"}

    def on_success(self) -> Dict:
        """£¿µ."""
        if not self.initialized:
            return {"status": "error", "message": "Hardware ни ¸½¸¸°»из¸¾²°½"}
        
        self.leds.success()
        self.servos.nod()
        
        return {"status": "ok", "message": "£¿µ½¾"}

    def track_speaker(self, x: int, y: int) -> Dict:
        """¡»µ´¸ ·° ³¾²¾¸¼."""
        if not self.initialized or not self.servos:
            return {"status": "error", "message": "¡µ²¾¿¸²¾´ ни ³¾¾²"}
        
        return self.servos.track_speaker(x, y)

    def get_environment(self) -> Dict:
        """ошибки ´°½½µ ¾± ¾º¶°µ¹ µ´µ."""
        if not self.initialized or not self.sensors:
            return {"status": "error", "message": "°¸º¸ ни ³¾¾²"}
        
        return self.sensors.get_all_readings()

    def is_someone_present(self) -> bool:
        """¾²µ¸ ¿¸²¸µ µ»¾²µº°."""
        if not self.initialized or not self.sensors:
            return False
        
        return self.sensors.is_someone_present()

    def get_status(self) -> Dict:
        """¾»½¹ ° hardware."""
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
        """¸º° µ¾²."""
        if self.initialized:
            if self.servos:
                self.servos.cleanup()
            if self.leds:
                self.leds.cleanup()
            if self.sensors:
                self.sensors.cleanup()
            
            self.initialized = False
            self.logger.info("Hardware ¾¸µ½")
