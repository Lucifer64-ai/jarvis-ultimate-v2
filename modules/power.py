"""
голосовые ¿¸°½¸µ¼ JARVIS
"""

import psutil
from typing import Dict


class PowerModule:
    """¾½¸¾¸½³ ¿¸°½¸."""

    def __init__(self, brain):
        self.brain = brain

    def get_battery_info(self) -> Dict:
        """½¾¼°¸ ¾ ±°°µµ."""
        battery = psutil.sensors_battery()
        if battery is None:
            return {"status": "ok", "available": False}

        return {
            "status": "ok",
            "available": True,
            "percent": battery.percent,
            "plugged": battery.power_plugged,
            "charging": battery.power_plugged and battery.percent < 100
        }

    def get_power_status(self) -> Dict:
        """¡° ¿¸°½¸."""
        battery = self.get_battery_info()
        if not battery.get("available"):
            return {"status": "ok", "source": "AC", "message": "¸°½¸µ ¾ µ¸"}

        if battery.get("plugged"):
            return {"status": "ok", "source": "AC", "percent": battery["percent"]}
        else:
            return {"status": "ok", "source": "battery", "percent": battery["percent"]}
