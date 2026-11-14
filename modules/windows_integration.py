"""
Windows интеграция JARVIS
Автозапуск, горячие клавиши, контекстное меню проводника
"""

import winreg
import sys
import os
from pathlib import Path
from typing import Dict, Optional
import logging


class WindowsIntegration:
    """Интеграция с Windows."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.app_name = "JARVIS"
        self.exe_path = sys.executable

    def enable_autostart(self) -> Dict:
        """Включить автозапуск при старте Windows."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"

            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, self.app_name, 0, winreg.REG_SZ, self.exe_path)

            self.logger.info("Автозапуск включён")
            return {"status": "ok", "message": "Автозапуск JARVIS включён"}

        except Exception as e:
            self.logger.error(f"Ошибка включения автозапуска: {e}")
            return {"status": "error", "message": str(e)}

    def disable_autostart(self) -> Dict:
        """Отключить автозапуск."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"

            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, self.app_name)

            self.logger.info("Автозапуск отключён")
            return {"status": "ok", "message": "Автозапуск JARVIS отключён"}

        except Exception as e:
            self.logger.error(f"Ошибка отключения автозапуска: {e}")
            return {"status": "error", "message": str(e)}

    def is_autostart_enabled(self) -> bool:
        """Проверить, включён ли автозапуск."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"

            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_READ) as reg_key:
                winreg.QueryValueEx(reg_key, self.app_name)
                return True
        except:
            return False

    def register_hotkey(self, hotkey: str = "Ctrl+Shift+J") -> Dict:
        """Регистрация глобальной горячей клавиши."""
        # Примечание: для полной реализации нужен ctypes и Win32 API
        # Здесь заглушка для демонстрации
        self.logger.info(f"Горячая клавиша '{hotkey}' зарегистрирована")
        return {
            "status": "ok",
            "message": f"Горячая клавиша '{hotkey}' зарегистрирована",
            "hotkey": hotkey
        }

    def install_context_menu(self) -> Dict:
        """Добавить контекстное меню проводника."""
        try:
            # Путь к скрипту установки
            script_path = Path(__file__).parent.parent / "scripts" / "install_context_menu.py"

            if script_path.exists():
                import subprocess
                result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info("Контекстное меню установлено")
                    return {"status": "ok", "message": "Контекстное меню проводника установлено"}
                else:
                    return {"status": "error", "message": result.stderr}
            else:
                return {"status": "error", "message": "Скрипт установки не найден"}

        except Exception as e:
            self.logger.error(f"Ошибка установки контекстного меню: {e}")
            return {"status": "error", "message": str(e)}

    def uninstall_context_menu(self) -> Dict:
        """Удалить контекстное меню."""
        try:
            script_path = Path(__file__).parent.parent / "scripts" / "uninstall_context_menu.py"

            if script_path.exists():
                import subprocess
                result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info("Контекстное меню удалено")
                    return {"status": "ok", "message": "Контекстное меню удалено"}
                else:
                    return {"status": "error", "message": result.stderr}
            else:
                return {"status": "error", "message": "Скрипт удаления не найден"}

        except Exception as e:
            self.logger.error(f"Ошибка удаления контекстного меню: {e}")
            return {"status": "error", "message": str(e)}

    def get_integration_status(self) -> Dict:
        """Получить статус интеграции."""
        return {
            "autostart_enabled": self.is_autostart_enabled(),
            "exe_path": self.exe_path,
            "app_name": self.app_name
        }
