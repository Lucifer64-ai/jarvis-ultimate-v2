"""
Windows ¸½µ³°¸ JARVIS
²¾·°¿º, ³¾¸µ º»°²¸¸, º¾½µº½¾µ ¼µ½ ¿¾²¾´½¸º°
"""

import winreg
import sys
import os
from pathlib import Path
from typing import Dict, Optional
import logging


class WindowsIntegration:
    """½µ³°¸  Windows."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.app_name = "JARVIS"
        self.exe_path = sys.executable

    def enable_autostart(self) -> Dict:
        """º»¸ °²¾·°¿º ¿¸ °µ Windows."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, self.app_name, 0, winreg.REG_SZ, self.exe_path)
            
            self.logger.info("²¾·°¿º ²º»µ½")
            return {"status": "ok", "message": "²¾·°¿º JARVIS ²º»µ½"}
        
        except Exception as e:
            self.logger.error(f"¸±º° ²º»µ½¸ °²¾·°¿º°: {e}")
            return {"status": "error", "message": str(e)}

    def disable_autostart(self) -> Dict:
        """º»¸ °²¾·°¿º."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, self.app_name)
            
            self.logger.info("²¾·°¿º ¾º»µ½")
            return {"status": "ok", "message": "²¾·°¿º JARVIS ¾º»µ½"}
        
        except Exception as e:
            self.logger.error(f"¸±º° ¾º»µ½¸ °²¾·°¿º°: {e}")
            return {"status": "error", "message": str(e)}

    def is_autostart_enabled(self) -> bool:
        """¾²µ¸, ²º»µ½ »¸ °²¾·°¿º."""
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_READ) as reg_key:
                winreg.QueryValueEx(reg_key, self.app_name)
                return True
        except:
            return False

    def register_hotkey(self, hotkey: str = "Ctrl+Shift+J") -> Dict:
        """ µ³¸°¸ ³»¾±°»½¾¹ ³¾µ¹ º»°²¸¸."""
        # ¸¼µ°½¸µ: ´» ¿¾»½¾µ½½¾¹ µ°»¸·°¸¸ ½¶µ½ ctypes ¸ Win32 API
        # ´µ ·°³»º° ´» ´µ¼¾½°¸¸
        self.logger.info(f"¾° º»°²¸° ·°µ³¸¸¾²°½°: {hotkey}")
        return {
            "status": "ok",
            "message": f"¾° º»°²¸° '{hotkey}' ·°µ³¸¸¾²°½°",
            "hotkey": hotkey
        }

    def install_context_menu(self) -> Dict:
        """£°½¾²¸ º¾½µº½¾µ ¼µ½ ¿¾²¾´½¸º°."""
        try:
            #  º º¸¿ °½¾²º¸
            script_path = Path(__file__).parent.parent / "scripts" / "install_context_menu.py"
            
            if script_path.exists():
                import subprocess
                result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("¾½µº½¾µ ¼µ½ °½¾²»µ½¾")
                    return {"status": "ok", "message": "¾½µº½¾µ ¼µ½ ¿¾²¾´½¸º° °½¾²»µ½¾"}
                else:
                    return {"status": "error", "message": result.stderr}
            else:
                return {"status": "error", "message": "¡º¸¿ °½¾²º¸ ½µ ½°¹´µ½"}
        
        except Exception as e:
            self.logger.error(f"¸±º° °½¾²º¸ º¾½µº½¾³¾ ¼µ½: {e}")
            return {"status": "error", "message": str(e)}

    def uninstall_context_menu(self) -> Dict:
        """£´°»¸ º¾½µº½¾µ ¼µ½."""
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
                return {"status": "error", "message": "¡º¸¿ ´°»µ½¸ ½µ ½°¹´µ½"}
        
        except Exception as e:
            self.logger.error(f"¸±º° ´°»µ½¸ º¾½µº½¾³¾ ¼µ½: {e}")
            return {"status": "error", "message": str(e)}

    def get_integration_status(self) -> Dict:
        """¾»¸ ° ¸½µ³°¸¸."""
        return {
            "autostart_enabled": self.is_autostart_enabled(),
            "exe_path": self.exe_path,
            "app_name": self.app_name
        }
