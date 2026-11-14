"""Safe, allowlisted desktop controls for JARVIS.

Only fixed keyboard shortcuts and system controls are exposed. Laptop Fn-key
layers are handled by firmware/vendor software and generally cannot be emitted
as a normal software key; F1-F12 are exposed as standard keys instead.
"""

from typing import Dict


class DesktopControlModule:
    """Basic keyboard and system controls for the local interactive desktop."""

    def __init__(self, brain):
        self.brain = brain

    @staticmethod
    def _pyautogui():
        try:
            import pyautogui
            return pyautogui
        except Exception as error:
            raise RuntimeError(
                "Библиотека pyautogui не установлена; установите пакет pyautogui и активируйте мышь"
            ) from error

    def minimize_all(self) -> Dict:
        try:
            self._pyautogui().hotkey("win", "d")
            return {"status": "ok", "message": "Свернул рабочий стол"}
        except Exception as error:
            return {"status": "error", "message": str(error)}

    def show_desktop(self) -> Dict:
        return self.minimize_all()

    def volume_up(self, steps: int = 3) -> Dict:
        return self._volume_key("volumeup", steps, "Громкость увеличена")

    def volume_down(self, steps: int = 3) -> Dict:
        return self._volume_key("volumedown", steps, "Громкость уменьшена")

    def _volume_key(self, key: str, steps: int, message: str) -> Dict:
        try:
            count = max(1, min(int(steps), 10))
            self._pyautogui().press(key, presses=count, interval=0.05)
            return {"status": "ok", "message": message}
        except Exception as error:
            return {"status": "error", "message": str(error)}

    def mute(self) -> Dict:
        try:
            self._pyautogui().press("volumemute")
            return {"status": "ok", "message": "Звук отключён"}
        except Exception as error:
            return {"status": "error", "message": str(error)}

    def lock_screen(self) -> Dict:
        try:
            import ctypes
            if not hasattr(ctypes, "windll"):
                return {"status": "error", "message": "Блокировка экрана доступна только на системах Windows"}
            ctypes.windll.user32.LockWorkStation()
            return {"status": "ok", "message": "Экран заблокирован"}
        except Exception as error:
            return {"status": "error", "message": str(error)}

    def shortcut(self, name: str) -> Dict:
        """Execute a supported non-destructive keyboard shortcut."""
        shortcuts = {
            "copy": ("ctrl", "c"),
            "paste": ("ctrl", "v"),
            "undo": ("ctrl", "z"),
            "select_all": ("ctrl", "a"),
            "print_screen": ("printscreen",),
            "snipping_tool": ("win", "shift", "s"),
            "num_lock": ("numlock",),
            "escape": ("esc",),
            "alt_tab": ("alt", "tab"),
            "task_manager": ("ctrl", "shift", "esc"),
            "refresh": ("f5",),
            "f1": ("f1",), "f2": ("f2",), "f3": ("f3",),
            "f4": ("f4",), "f5": ("f5",), "f6": ("f6",),
            "f7": ("f7",), "f8": ("f8",), "f9": ("f9",),
            "f10": ("f10",), "f11": ("f11",), "f12": ("f12",),
        }
        keys = shortcuts.get(name)
        if not keys:
            return {"status": "error", "message": "Эта комбинация клавиш не разрешена"}
        try:
            pyautogui = self._pyautogui()
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            return {"status": "ok", "message": f"Выполнена команда клавиатуры: {name}"}
        except Exception as error:
            return {"status": "error", "message": str(error)}
