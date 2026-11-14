"""
Обработчик голосовых команд JARVIS
"""

from typing import Dict, Optional
import re


class CommandHandler:
    """Обработчик голосовых команд."""

    def __init__(self, brain):
        self.brain = brain
        self.commands = self._register_commands()

    def _register_commands(self) -> Dict:
        """Регистрация команд."""
        return {
            # Системные команды
            r"выключи (компьютер|пк)": ("system", "shutdown"),
            r"перезагрузи (компьютер|пк)": ("system", "restart"),
            r"отмени выключение": ("system", "cancel_shutdown"),
            r"заблокируй (экран|компьютер)": ("system", "lock_screen"),
            r"спящий режим": ("system", "sleep"),

            # Управление окнами рабочего стола
            r"(покажи|окно) рабочий стол|сверни все окна|сверни окна": ("desktop", "show_desktop"),
            r"сделай громче|увеличь громкость|громче": ("desktop", "volume_up"),
            r"сделай тише|уменьши громкость|тише": ("desktop", "volume_down"),
            r"без звука|mute|выключи звук": ("desktop", "mute"),
            r"заблокируй экран|заблокируй экран|lock screen": ("desktop", "lock_screen"),
            r"копировать|copy": ("desktop", "shortcut"),
            r"вставить|paste": ("desktop", "shortcut"),
            r"отменить|undo": ("desktop", "shortcut"),
            r"выделить всё|select all": ("desktop", "shortcut"),

            # Информация
            r"который час|время|сколько времени": ("info", "time"),
            r"какая (дата|сегодня)": ("info", "date"),
            r"какая погода": ("info", "weather"),
            r"статус системы": ("info", "system_status"),
            r"загрузка процессора": ("info", "cpu_usage"),
            r"состояние батареи": ("info", "battery"),

            # Приложения
            r"открой (блокнот|notepad)": ("app", "open_notepad"),
            r"открой калькулятор": ("app", "open_calculator"),
            r"открой youtube": ("app", "open_youtube"),
            r"открой github": ("app", "open_github"),

            # Управление
            r"громкость (\d+)": ("control", "set_volume"),
            r"яркость (\d+)": ("control", "set_brightness"),
            r"сверни все окна": ("control", "minimize_all"),
            r"покажи рабочий стол": ("control", "show_desktop"),

            # Сеть
            r"сеть скорость|скорость интернета": ("network", "speed_test"),
            r"какой (ip|айпи) адрес": ("network", "get_ip"),
        }

    def parse_command(self, text: str) -> Optional[Dict]:
        """Разбор команд."""
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
                    # для copy/paste/undo/select all, передаём имя команды как параметр
                    result["shortcut_name"] = text_lower

                return result

        return None

    def execute(self, text: str) -> Dict:
        """Выполнение команд."""
        command = self.parse_command(text)

        if not command:
            return {"status": "error", "message": "Команда не распознана"}

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
                            return {"status": "error", "message": "Комбинация не поддерживается"}
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

            return {"status": "error", "message": "Действие не реализовано"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_shortcut_name(self, text: str) -> str:
        text_lower = text.lower().strip()
        mapping = {
            "копировать": "copy",
            "copy": "copy",
            "вставить": "paste",
            "paste": "paste",
            "отменить": "undo",
            "undo": "undo",
            "выделить всё": "select_all",
            "select all": "select_all",
        }
        for key, value in mapping.items():
            if key in text_lower:
                return value
        return ""

    def _handle_info(self, action: str) -> Dict:
        """Обработка информационных команд."""
        from datetime import datetime

        if action == "time":
            now = datetime.now()
            return {"status": "ok", "message": f"Сейчас {now.strftime('%H:%M')}"}

        elif action == "date":
            now = datetime.now()
            return {"status": "ok", "message": f"Сегодня {now.strftime('%d %B %Y')}"}

        elif action == "system_status":
            hardware = self.brain.modules.get("hardware")
            if hardware:
                report = hardware.get_full_report()
                return {"status": "ok", "data": report}

        elif action == "cpu_usage":
            hardware = self.brain.modules.get("hardware")
            if hardware:
                cpu_info = hardware.get_cpu_info()
                return {"status": "ok", "message": f"Загрузка процессора {cpu_info['usage']}%"}

        elif action == "battery":
            power = self.brain.modules.get("power")
            if power:
                battery = power.get_battery_info()
                if battery.get("available"):
                    return {"status": "ok", "message": f"Заряд батареи {battery['percent']}%"}
                else:
                    return {"status": "ok", "message": "Батарея не обнаружена"}

        return {"status": "error", "message": "Информация недоступна"}

    def _handle_app(self, action: str) -> Dict:
        """Обработка команд открытия приложений."""
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
                return {"status": "ok", "message": f"Открываю {action.replace('open_', '')}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        return {"status": "error", "message": "Приложение не найдено"}

    def _handle_control(self, action: str, params: tuple = None) -> Dict:
        """Обработка команд управления."""
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
                return {"status": "error", "message": "Управление громкостью недоступно"}
            try:
                volume_level = int(params[0]) / 100
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)
                volume.SetMasterVolumeLevelScalar(volume_level, None)
                return {"status": "ok", "message": f"Громкость установлена на {params[0]}%"}
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

        return {"status": "error", "message": "Команда не реализована"}

