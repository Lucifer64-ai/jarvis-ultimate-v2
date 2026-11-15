"""
Clean Desktop Mode - Скрытие иконок рабочего стола
"""

import ctypes
from typing import Dict, Optional
import logging

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None


class CleanDesktop:
    """Управление видимостью иконок рабочего стола."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.icons_hidden = False

    def _win32_available(self) -> bool:
        """Проверить доступны ли win32-модули (только в Windows)."""
        return win32gui is not None and win32con is not None

    def _get_desktop_window(self):
        """Получить окно рабочего стола (SysListView32)."""
        if not self._win32_available():
            return None
        progman = win32gui.FindWindow("Progman", None)
        defview = win32gui.FindWindowEx(progman, 0, "SHELLDLL_DefView", None)
        sys_listview = win32gui.FindWindowEx(defview, 0, "SysListView32", None)
        return sys_listview

    def hide_icons(self) -> Dict:
        """Скрыть все иконки рабочего стола."""
        if not self._win32_available():
            return {"status": "error", "message": "win32gui недоступен (только для Windows)"}
        try:
            sys_listview = self._get_desktop_window()

            if sys_listview:
                # Скрываем окно с иконками
                win32gui.ShowWindow(sys_listview, win32con.SW_HIDE)
                self.icons_hidden = True
                self.logger.info("Иконки рабочего стола скрыты")
                return {"status": "ok", "message": "Иконки скрыты. Рабочий стол чист."}
            else:
                return {"status": "error", "message": "Не удалось найти окно рабочего стола"}

        except Exception as e:
            self.logger.error(f"Ошибка скрытия иконок: {e}")
            return {"status": "error", "message": str(e)}

    def show_icons(self) -> Dict:
        """Показать иконки рабочего стола."""
        if not self._win32_available():
            return {"status": "error", "message": "win32gui недоступен (только для Windows)"}
        try:
            sys_listview = self._get_desktop_window()

            if sys_listview:
                win32gui.ShowWindow(sys_listview, win32con.SW_SHOW)
                self.icons_hidden = False
                self.logger.info("Иконки рабочего стола показаны")
                return {"status": "ok", "message": "Иконки показаны."}
            else:
                return {"status": "error", "message": "Не удалось найти окно рабочего стола"}

        except Exception as e:
            self.logger.error(f"Ошибка показа иконок: {e}")
            return {"status": "error", "message": str(e)}

    def toggle_icons(self) -> Dict:
        """Переключить видимость иконок."""
        if self.icons_hidden:
            return self.show_icons()
        else:
            return self.hide_icons()

    def is_hidden(self) -> bool:
        """Проверить, скрыты ли иконки."""
        return self.icons_hidden

    def hide_taskbar(self) -> Dict:
        """Скрыть панель задач."""
        if not self._win32_available():
            return {"status": "error", "message": "win32gui недоступен (только для Windows)"}
        try:
            taskbar = win32gui.FindWindow("Shell_traywnd", None)
            if taskbar:
                win32gui.ShowWindow(taskbar, win32con.SW_HIDE)
                self.logger.info("Панель задач скрыта")
                return {"status": "ok", "message": "Панель задач скрыта."}
            return {"status": "error", "message": "Панель задач не найдена"}
        except Exception as e:
            self.logger.error(f"Ошибка скрытия панели задач: {e}")
            return {"status": "error", "message": str(e)}

    def show_taskbar(self) -> Dict:
        """Показать панель задач."""
        if not self._win32_available():
            return {"status": "error", "message": "win32gui недоступен (только для Windows)"}
        try:
            taskbar = win32gui.FindWindow("Shell_traywnd", None)
            if taskbar:
                win32gui.ShowWindow(taskbar, win32con.SW_SHOW)
                self.logger.info("Панель задач показана")
                return {"status": "ok", "message": "Панель задач показана."}
            return {"status": "error", "message": "Панель задач не найдена"}
        except Exception as e:
            self.logger.error(f"Ошибка показа панели задач: {e}")
            return {"status": "error", "message": str(e)}

    def enable_clean_mode(self) -> Dict:
        """Включить режим чистого рабочего стола."""
        result1 = self.hide_icons()
        result2 = self.hide_taskbar()

        if result1["status"] == "ok" and result2["status"] == "ok":
            return {"status": "ok", "message": "Режим чистого рабочего стола включен. Используйте JARVIS для управления."}
        else:
            return {"status": "partial", "message": "Частично включено", "icons": result1, "taskbar": result2}

    def disable_clean_mode(self) -> Dict:
        """Выключить режим чистого рабочего стола."""
        result1 = self.show_icons()
        result2 = self.show_taskbar()

        if result1["status"] == "ok" and result2["status"] == "ok":
            return {"status": "ok", "message": "Режим чистого рабочего стола выключен."}
        else:
            return {"status": "partial", "message": "Частично выключено", "icons": result1, "taskbar": result2}
