"""
голосовые µµ¾¼ Windows JARVIS
"""

import winreg
from typing import Dict, Optional


class RegistryModule:
    """голосовые µµ¾¼ Windows."""

    def __init__(self, brain):
        self.brain = brain

    def read_value(self, path: str, name: str) -> Dict:
        """¾¸° ·наµ½¸µ из µµ°."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
            value, reg_type = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return {"status": "ok", "value": value, "type": reg_type}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def write_value(self, path: str, name: str, value, reg_type=winreg.REG_SZ) -> Dict:
        """°¿¸° ·наµ½¸µ ² µµ."""
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
            winreg.SetValueEx(key, name, 0, reg_type, value)
            winreg.CloseKey(key)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_value(self, path: str, name: str) -> Dict:
        """£´°»¸ ·наµ½¸µ из µµ°."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
