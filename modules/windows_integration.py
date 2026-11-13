"""
Windows и½µ³°и JARVIS
в¾·°¿º, ³¾иµ º»°вии, º¾½µº½¾µ ¼µ½ ¿¾в¾´½иº°
"""

import winreg
import sys
import os
from pathlib import Path
from typing import Dict, Optional
import logging


class WindowsIntegration:
    """½µ³°и  Windows."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.app_name = "JARVIS"
        self.exe_path = sys.executable

    def enable_autostart(self) -> Dict:
        """º»и °в¾·°¿º ¿и °µ Windows."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, self.app_name, 0, winreg.REG_SZ, self.exe_path)
            
            self.logger.info("в¾·°¿º вº»µ½")
            return {"status": "ok", "message": "в¾·°¿º JARVIS вº»µ½"}
        
        except Exception as e:
            self.logger.error(f"агента вº»µ½и °в¾·°¿º°: {e}")
            return {"status": "error", "message": str(e)}

    def disable_autostart(self) -> Dict:
        """º»и °в¾·°¿º."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, self.app_name)
            
            self.logger.info("в¾·°¿º ¾º»µ½")
            return {"status": "ok", "message": "в¾·°¿º JARVIS ¾º»µ½"}
        
        except Exception as e:
            self.logger.error(f"агента ¾º»µ½и °в¾·°¿º°: {e}")
            return {"status": "error", "message": str(e)}

    def is_autostart_enabled(self) -> bool:
        """¾вµи, вº»µ½ »и °в¾·°¿º."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_READ) as reg_key:
                winreg.QueryValueEx(reg_key, self.app_name)
                return True
        except:
            return False

    def register_hotkey(self, hotkey: str = "Ctrl+Shift+J") -> Dict:
        """ µ³и°и ³»¾±°»½¾¹ ³¾µ¹ º»°вии."""
        # и¼µ°½иµ: ´» ¿¾»½¾µ½½¾¹ µ°»и·°ии ½¶µ½ ctypes и Win32 API
        # ´µ ·°³»º° ´» ´µ¼¾½°ии
        self.logger.info(f"¾° º»°ви° ·°µ³ии¾в°½°: {hotkey}")
        return {
            "status": "ok",
            "message": f"¾° º»°ви° '{hotkey}' ·°µ³ии¾в°½°",
            "hotkey": hotkey
        }

    def install_context_menu(self) -> Dict:
        """£°½¾ви º¾½µº½¾µ ¼µ½ ¿¾в¾´½иº°."""
        try:
            #  º ºи¿ °½¾вºи
            script_path = Path(__file__).parent.parent / "scripts" / "install_context_menu.py"
            
            if script_path.exists():
                import subprocess
                result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("¾½µº½¾µ ¼µ½ °½¾в»µ½¾")
                    return {"status": "ok", "message": "¾½µº½¾µ ¼µ½ ¿¾в¾´½иº° °½¾в»µ½¾"}
                else:
                    return {"status": "error", "message": result.stderr}
            else:
                return {"status": "error", "message": "¡ºи¿ °½¾вºи ни ½°¹´µ½"}
        
        except Exception as e:
            self.logger.error(f"агента °½¾вºи º¾½µº½¾³¾ ¼µ½: {e}")
            return {"status": "error", "message": str(e)}

    def uninstall_context_menu(self) -> Dict:
        """£´°»и º¾½µº½¾µ ¼µ½."""
        try:
            script_path = Path(__file__).parent.parent / "scripts" / "uninstall_context_menu.py"
            
            if script_path.exists():
                import subprocess
                result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("¾½µº½¾µ ¼µ½ ´°»µ½¾")
                    return {"status": "ok", "message": "¾½µº½¾µ ¼µ½ ´°»µ½¾"}
                else:
                    return {"status": "error", "message": result.stderr}
            else:
                return {"status": "error", "message": "¡ºи¿ ´°»µ½и ни ½°¹´µ½"}
        
        except Exception as e:
            self.logger.error(f"агента ´°»µ½и º¾½µº½¾³¾ ¼µ½: {e}")
            return {"status": "error", "message": str(e)}

    def get_integration_status(self) -> Dict:
        """¾»и ° и½µ³°ии."""
        return {
            "autostart_enabled": self.is_autostart_enabled(),
            "exe_path": self.exe_path,
            "app_name": self.app_name
        }
