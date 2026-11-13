"""
голосовые ¾ºна¼¸ JARVIS
"""

import win32gui
import win32con
from typing import Dict, List


class WindowModule:
    """голосовые ¾ºна¼¸ Windows."""

    def __init__(self, brain):
        self.brain = brain

    def list_windows(self) -> List[Dict]:
        """¡¿¸¾º ¾º ¾º¾½."""
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
        """¡²µ½ ²µ ¾ºна."""
        try:
            import pyautogui
            pyautogui.hotkey('win', 'd')
            return {"status": "ok", "message": "µ ¾ºна ²½"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def show_desktop(self) -> Dict:
        """¾º°·° °±¾¸¹ ¾»."""
        return self.minimize_all()

    def close_window(self, title: str) -> Dict:
        """°º ¾º½¾ ¿¾ ·°³¾»¾²º."""
        def callback(hwnd, target):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if target.lower() in window_title.lower():
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    return True
            return False

        try:
            win32gui.EnumWindows(lambda hwnd, _: callback(hwnd, title), None)
            return {"status": "ok", "message": f"º½¾ '{title}' ·°º¾"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
