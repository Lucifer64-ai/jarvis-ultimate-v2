"""
Системные операции JARVIS
"""

import os
import subprocess
import ctypes
from typing import Dict


class SystemModule:
    """Управление системными операциями."""

    def __init__(self, brain):
        self.brain = brain

    def shutdown(self) -> Dict:
        """Выключение компьютера."""
        try:
            os.system("shutdown /s /t 60")
            return {"status": "ok", "message": "Компьютер будет выключен через 60 секунд"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def restart(self) -> Dict:
        """Перезагрузка компьютера."""
        try:
            os.system("shutdown /r /t 60")
            return {"status": "ok", "message": "Компьютер будет перезагружен через 60 секунд"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cancel_shutdown(self) -> Dict:
        """Отмена выключения."""
        try:
            os.system("shutdown /a")
            return {"status": "ok", "message": "Выключение отменено"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def lock_screen(self) -> Dict:
        """Блокировка экрана."""
        try:
            ctypes.windll.user32.LockWorkStation()
            return {"status": "ok", "message": "Экран заблокирован"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def sleep(self) -> Dict:
        """Спящий режим."""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return {"status": "ok", "message": "Переход в спящий режим"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def hibernate(self) -> Dict:
        """Гибернация."""
        try:
            os.system("shutdown /h")
            return {"status": "ok", "message": "Переход в режим гибернации"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def logoff(self) -> Dict:
        """Выход из системы."""
        try:
            os.system("shutdown /l")
            return {"status": "ok", "message": "Выход из системы"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
