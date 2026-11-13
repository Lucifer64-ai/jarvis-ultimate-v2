"""Optional keyboard RGB control through a local OpenRGB SDK server.

RGB keyboard control is vendor/model dependent. This adapter only connects to
OpenRGB on localhost; it does not search the network or run shell commands.
Requires `openrgb-python` and the OpenRGB SDK server to be enabled locally.
"""

from typing import Dict


class KeyboardLightingModule:
    def __init__(self, brain):
        self.brain = brain

    def set_color(self, red: int, green: int, blue: int, device_index: int | None = None) -> Dict:
        try:
            rgb = tuple(max(0, min(255, int(value))) for value in (red, green, blue))
        except (TypeError, ValueError):
            return {"status": "error", "message": "¦²µ ´¾»¶µ½ ± ·°´°½ µ¼ ¸»°¼¸ ¾ 0 ´¾ 255"}

        try:
            from openrgb import OpenRGBClient
            from openrgb.utils import RGBColor
        except ImportError:
            return {
                "status": "unavailable",
                "message": "» RGB-º»°²¸° °½¾²¸µ openrgb-python ¸ ²º»¸µ »¾º°»½¹ SDK Server ² OpenRGB.",
            }

        try:
            client = OpenRGBClient("127.0.0.1", 6742, name="JARVIS")
            devices = list(client.devices)
            keyboards = [device for device in devices if "keyboard" in str(getattr(device, "type", "")).lower()]
            if not keyboards:
                keyboards = [device for device in devices if "keyboard" in str(getattr(device, "name", "")).lower()]
            if not keyboards:
                return {"status": "unavailable", "message": "OpenRGB ни ¾±на¶¸» ¾²¼µ¸¼ º»°²¸°"}

            selected_index = 0 if device_index is None else int(device_index)
            if selected_index < 0 or selected_index >= len(keyboards):
                return {"status": "error", "message": "½´µº º»°²¸° ²ни ´¸°¿°·¾на", "count": len(keyboards)}

            keyboard = keyboards[selected_index]
            keyboard.set_color(RGBColor(*rgb))
            return {
                "status": "ok",
                "message": f"¦²µ º»°²¸° °½¾²»µ½: RGB{rgb}",
                "device": str(getattr(keyboard, "name", "keyboard")),
            }
        except Exception as error:
            self.brain.logger.warning("µ ´°»¾ из¼µ½¸ ¿¾´²µº º»°²¸°: %s", error)
            return {
                "status": "error",
                "message": "µ ´°»¾ ¿¾´º»¸ º OpenRGB. ¾²µµ SDK Server ¸ ¾²¼µ¸¼¾ º»°²¸°.",
            }

    def off(self, device_index: int | None = None) -> Dict:
        return self.set_color(0, 0, 0, device_index)
