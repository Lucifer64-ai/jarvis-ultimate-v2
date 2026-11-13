"""
¡¸µ¼½µ ¾¿µ°¸¸ JARVIS
"""

import os
import subprocess
import ctypes
from typing import Dict


class SystemModule:
    """голосовые ¸µ¼½¼¸ ¾¿µ°¸¼¸."""

    def __init__(self, brain):
        self.brain = brain

    def shutdown(self) -> Dict:
        """º»µ½¸µ º¾¼¿µ°."""
        try:
            os.system("shutdown /s /t 60")
            return {"status": "ok", "message": "¾¼¿µ ±´µ ²º»µ½ µµ· 60 µº½´"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def restart(self) -> Dict:
        """µµ·°³·º° º¾¼¿µ°."""
        try:
            os.system("shutdown /r /t 60")
            return {"status": "ok", "message": "¾¼¿µ ±´µ ¿µµ·°³¶µ½ µµ· 60 µº½´"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cancel_shutdown(self) -> Dict:
        """¼µна ²º»µ½¸."""
        try:
            os.system("shutdown /a")
            return {"status": "ok", "message": "º»µ½¸µ ¾¼µни½¾"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def lock_screen(self) -> Dict:
        """»¾º¸¾²º° º°на."""
        try:
            ctypes.windll.user32.LockWorkStation()
            return {"status": "ok", "message": "­º°½ ·°±»¾º¸¾²°½"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def sleep(self) -> Dict:
        """¡¿¸¹ µ¶¸¼."""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return {"status": "ok", "message": "µµ¾´ ² ¿¸¹ µ¶¸¼"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def hibernate(self) -> Dict:
        """¸±µна¸."""
        try:
            os.system("shutdown /h")
            return {"status": "ok", "message": "µµ¾´ ² µ¶¸¼ ³¸±µна¸¸"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def logoff(self) -> Dict:
        """¾´ из ¸µ¼."""
        try:
            os.system("shutdown /l")
            return {"status": "ok", "message": "¾´ из ¸µ¼"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
