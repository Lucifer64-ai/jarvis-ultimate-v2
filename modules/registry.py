"""
Управление реестром Windows JARVIS
"""

from typing import Dict, Optional

try:
    import winreg
except ImportError:
    winreg = None


class RegistryModule:
    """Управление реестром Windows."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

    def _check_winreg(self) -> bool:
        """Проверить доступен ли winreg."""
        if winreg is None:
            self.logger.warning("winreg недоступен (только для Windows)")
            return False
        return True

    def read_value(self, path: str, name: str) -> Dict:
        """Прочитать значение из реестра."""
        if not self._check_winreg():
            return {"status": "error", "message": "winreg недоступен (только для Windows)"}
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
            value, reg_type = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return {"status": "ok", "value": value, "type": reg_type}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def write_value(self, path: str, name: str, value, reg_type=None) -> Dict:
        """Записать значение в реестр."""
        if not self._check_winreg():
            return {"status": "error", "message": "winreg недоступен (только для Windows)"}
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
            winreg.SetValueEx(key, name, 0, reg_type or winreg.REG_SZ, value)
            winreg.CloseKey(key)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_value(self, path: str, name: str) -> Dict:
        """Удалить значение из реестра."""
        if not self._check_winreg():
            return {"status": "error", "message": "winreg недоступен (только для Windows)"}
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
