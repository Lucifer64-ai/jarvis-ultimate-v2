"""
±°±¾¸º ³¾»¾¾² º¾¼°½´ JARVIS
"""

from typing import Dict, Optional
import re


class CommandHandler:
    """±°±¾º° ³¾»¾¾² º¾¼°½´."""

    def __init__(self, brain):
        self.brain = brain
        self.commands = self._register_commands()

    def _register_commands(self) -> Dict:
        """ µ³¸°¸ º¾¼°½´."""
        return {
            # ¡¸µ¼½µ º¾¼°½´
            r"²º»¸ (º¾¼¿µ|¿º)": ("system", "shutdown"),
            r"¿µµ·°³·¸ (º¾¼¿µ|¿º)": ("system", "restart"),
            r"¾¼µ½¸ ²º»µ½¸µ": ("system", "cancel_shutdown"),
            r"·°±»¾º¸¹ (º°½|º¾¼¿µ)": ("system", "lock_screen"),
            r"¿¸¹ µ¶¸¼": ("system", "sleep"),

            # ¾»½¹ º¾½¾» °±¾µ³¾ ¾»°/
            r"(¿¾º°¶¸|¾º¾¹) °±¾¸¹ ¾»|²µ½¸ ²µ ¾º½°|²µ½¸ ¾º½°": ("desktop", "show_desktop"),
            r"´µ»°¹ ³¾¼µ|²µ»¸ ³¾¼º¾|³¾¼µ": ("desktop", "volume_up"),
            r"´µ»°¹ ¸µ|¼µ½¸ ³¾¼º¾|¸µ": ("desktop", "volume_down"),
            r"±µ· ·²º°|mute|²º»¸ ·²º": ("desktop", "mute"),
            r"·°±»¾º¸¹ º°½|±»¾º¸¹ º°½|lock screen": ("desktop", "lock_screen"),
            r"º¾¿¸¾²°|copy": ("desktop", "shortcut"),
            r"²°²¸|paste": ("desktop", "shortcut"),
            r"¾¼µ½¸|undo": ("desktop", "shortcut"),
            r"²´µ»¸ ²|select all": ("desktop", "shortcut"),

            # ½¾¼°¸
            r"º¾¾¹ °|²µ¼|º¾»º¾ ²µ¼µ½¸": ("info", "time"),
            r"º°º° (´°°|µ³¾´½)": ("info", "date"),
            r"º°º° ¿¾³¾´°": ("info", "weather"),
            r"° ¸µ¼": ("info", "system_status"),
            r"·°³·º° ¿¾µ¾°": ("info", "cpu_usage"),
            r"¾¾½¸µ ±°°µ¸": ("info", "battery"),

            # ¸»¾¶µ½¸
            r"¾º¾¹ (±»¾º½¾|notepad)": ("app", "open_notepad"),
            r"¾º¾¹ º°»º»¾": ("app", "open_calculator"),
            r"¾º¾¹ youtube": ("app", "open_youtube"),
            r"¾º¾¹ github": ("app", "open_github"),

            # £¿°²»µ½¸µ
            r"³¾¼º¾ (\d+)": ("control", "set_volume"),
            r"º¾ (\d+)": ("control", "set_brightness"),
            r"²µ½¸ ²µ ¾º½°": ("control", "minimize_all"),
            r"¿¾º°¶¸ °±¾¸¹ ¾»": ("control", "show_desktop"),

            # ¡µ
            r"µ º¾¾¸|º¾¾ ¸½µ½µ°": ("network", "speed_test"),
            r"º°º¾¹ (ip|°¹¿¸) °´µ": ("network", "get_ip"),
        }

    def parse_command(self, text: str) -> Optional[Dict]:
        """ °·±¾ º¾¼°½´."""
        text_lower = text.lower().strip()

        for pattern, (category, action) in self.commands.items():
            match = re.match(pattern, text_lower)
            if match:
                result = {
                    "category": category,
                    "action": action,
                    "original": text,
                }

                if match.groups():
                    result["params"] = match.groups()

                if category in {"desktop", "control"} and action == "shortcut":
                    # ´» copy/paste/undo/select all, ¿µµ´°¼ ¸¼ º¾¼°½´ º°º ¿°°¼µ
                    result["shortcut_name"] = text_lower

                return result

        return None

    def execute(self, text: str) -> Dict:
        """¿¾»½µ½¸µ º¾¼°½´."""
        command = self.parse_command(text)

        if not command:
            return {"status": "error", "message": "¾¼°½´° ½µ °¿¾·½°½°"}

        category = command["category"]
        action = command["action"]

        try:
            if category == "system":
                module = self.brain.modules.get("system")
                if module and hasattr(module, action):
                    return getattr(module, action)()

            elif category == "desktop":
                module = self.brain.modules.get("desktop_control")
                if module and hasattr(module, action):
                    if action == "shortcut":
                        shortcut_name = self._extract_shortcut_name(text)
                        if not shortcut_name:
                            return {"status": "error", "message": "¾¼±¸½°¸ ½µ ¿¾´´µ¶¸²°µ"}
                        return module.shortcut(shortcut_name)
                    return getattr(module, action)()
                # fallback to legacy desktop/system actions
                legacy = self.brain.modules.get("system")
                if legacy and hasattr(legacy, action):
                    return getattr(legacy, action)()

            elif category == "info":
                return self._handle_info(action)

            elif category == "app":
                return self._handle_app(action)

            elif category == "control":
                return self._handle_control(action, command.get("params"))

            elif category == "network":
                module = self.brain.modules.get("network")
                if module and hasattr(module, action):
                    return getattr(module, action)()

            return {"status": "error", "message": "µ¹²¸µ ½µ µ°»¸·¾²°½¾"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_shortcut_name(self, text: str) -> str:
        text_lower = text.lower().strip()
        mapping = {
            "º¾¿¸¾²°": "copy",
            "copy": "copy",
            "²°²¸": "paste",
            "paste": "paste",
            "¾¼µ½¸": "undo",
            "undo": "undo",
            "²´µ»¸ ²": "select_all",
            "select all": "select_all",
        }
        for key, value in mapping.items():
            if key in text_lower:
                return value
        return ""

    def _handle_info(self, action: str) -> Dict:
        """±°±¾º° ¸½¾¼°¸¾½½ º¾¼°½´."""
        from datetime import datetime

        if action == "time":
            now = datetime.now()
            return {"status": "ok", "message": f"¡µ¹° {now.strftime('%H:%M')}"}

        elif action == "date":
            now = datetime.now()
            return {"status": "ok", "message": f"¡µ³¾´½ {now.strftime('%d %B %Y')}"}

        elif action == "system_status":
            hardware = self.brain.modules.get("hardware")
            if hardware:
                report = hardware.get_full_report()
                return {"status": "ok", "data": report}

        elif action == "cpu_usage":
            hardware = self.brain.modules.get("hardware")
            if hardware:
                cpu_info = hardware.get_cpu_info()
                return {"status": "ok", "message": f"°³·º° ¿¾µ¾° {cpu_info['usage']}%"}

        elif action == "battery":
            power = self.brain.modules.get("power")
            if power:
                battery = power.get_battery_info()
                if battery.get("available"):
                    return {"status": "ok", "message": f"°´ ±°°µ¸ {battery['percent']}%"}
                else:
                    return {"status": "ok", "message": "°°µ ½µ ¾±½°¶µ½°"}

        return {"status": "error", "message": "½¾¼°¸ ½µ´¾¿½°"}

    def _handle_app(self, action: str) -> Dict:
        """±°±¾º° º¾¼°½´ ¾º¸ ¿¸»¾¶µ½¸¹."""
        import subprocess

        apps = {
            "open_notepad": "notepad",
            "open_calculator": "calc",
            "open_youtube": "https://youtube.com",
            "open_github": "https://github.com",
        }

        if action in apps:
            target = apps[action]
            try:
                if target.startswith("http"):
                    subprocess.Popen(["cmd", "/c", "start", "", target], shell=True)
                else:
                    subprocess.Popen([target])
                return {"status": "ok", "message": f"º²° {action.replace('open_', '')}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        return {"status": "error", "message": "¸»¾¶µ½¸µ ½µ ½°¹´µ½¾"}

    def _handle_control(self, action: str, params: tuple = None) -> Dict:
        """±°±¾º° º¾¼°½´ ¿°²»µ½¸."""
        try:
            import pyautogui
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
        except Exception:
            pyautogui = None
            AudioUtilities = None
            IAudioEndpointVolume = None
            CLSCTX_ALL = None

        if action == "set_volume" and params:
            if pyautogui is None or AudioUtilities is None:
                return {"status": "error", "message": "£¿°²»µ½¸µ ³¾¼º¾ ½µ´¾¿½¾"}
            try:
                volume_level = int(params[0]) / 100
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)
                volume.SetMasterVolumeLevelScalar(volume_level, None)
                return {"status": "ok", "message": f"¾¼º¾ °½¾²»µ½° ½° {params[0]}%"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif action == "minimize_all":
            desktop = self.brain.modules.get("desktop_control")
            if desktop:
                return desktop.minimize_all()

        elif action == "show_desktop":
            desktop = self.brain.modules.get("desktop_control")
            if desktop:
                return desktop.show_desktop()

        return {"status": "error", "message": "¾¼°½´° ½µ µ°»¸·¾²°½°"}

