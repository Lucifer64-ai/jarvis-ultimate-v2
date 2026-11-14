"""
Управление окнами JARVIS
"""

import win32gui
import win32con
from typing import Dict, List


class WindowModule:
    """Управление окнами Windows."""

    def __init__(self, brain):
        self.brain = brain

    def list_windows(self) -> List[Dict]:
        """Список активных окон."""
        windows = []

        def callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    results.append({
                        "hwnd": hwnd,
                        "title": title
                    })

        win32gui.EnumWindows(callback, windows)
        return windows

    def minimize_all(self) -> Dict:
        """Свернуть все окна."""
        try:
            import pyautogui
            pyautogui.hotkey('win', 'd')
            return {"status": "ok", "message": "Все окна свёрнуты"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def show_desktop(self) -> Dict:
        """Показать рабочий стол."""
        return self.minimize_all()

    def close_window(self, title: str) -> Dict:
        """Закрыть окно по заголовку."""
        def callback(hwnd, target):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if target.lower() in window_title.lower():
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    return True
            return False

        try:
            win32gui.EnumWindows(lambda hwnd, _: callback(hwnd, title), None)
            return {"status": "ok", "message": f"Окно '{title}' закрыто"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
