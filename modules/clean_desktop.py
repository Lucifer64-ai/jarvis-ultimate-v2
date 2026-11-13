"""
Clean Desktop Mode - ¡º¸µ ¸º¾½¾º °±¾µ³¾ ¾»°
"""

import ctypes
import win32gui
import win32con
from typing import Dict, Optional
import logging


class CleanDesktop:
    """£¿°²»µ½¸µ ²¸´¸¼¾ ¸º¾½¾º °±¾µ³¾ ¾»°."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.icons_hidden = False

    def hide_icons(self) -> Dict:
        """¡º ²µ ¸º¾½º¸ °±¾µ³¾ ¾»°."""
        try:
            # ¾»°µ¼ ¾º½¾ °±¾µ³¾ ¾»°
            progman = win32gui.FindWindow("Progman", None)
            defview = win32gui.FindWindowEx(progman, 0, "SHELLDLL_DefView", None)
            sys_listview = win32gui.FindWindowEx(defview, 0, "SysListView32", None)
            
            if sys_listview:
                # ¡º²°µ¼ ¾º½¾  ¸º¾½º°¼¸
                win32gui.ShowWindow(sys_listview, win32con.SW_HIDE)
                self.icons_hidden = True
                self.logger.info("º¾½º¸ °±¾µ³¾ ¾»° º")
                return {"status": "ok", "message": "º¾½º¸ º.  °±¾¸¹ ¾» ¸."}
            else:
                return {"status": "error", "message": "µ ´°»¾ ½°¹¸ ¾º½¾ °±¾µ³¾ ¾»°"}
        
        except Exception as e:
            self.logger.error(f"¸±º° º¸ ¸º¾½¾º: {e}")
            return {"status": "error", "message": str(e)}

    def show_icons(self) -> Dict:
        """¾º°·° ¸º¾½º¸ °±¾µ³¾ ¾»°."""
        try:
            progman = win32gui.FindWindow("Progman", None)
            defview = win32gui.FindWindowEx(progman, 0, "SHELLDLL_DefView", None)
            sys_listview = win32gui.FindWindowEx(defview, 0, "SysListView32", None)
            
            if sys_listview:
                win32gui.ShowWindow(sys_listview, win32con.SW_SHOW)
                self.icons_hidden = False
                self.logger.info("º¾½º¸ °±¾µ³¾ ¾»° ¿¾º°·°½")
                return {"status": "ok", "message": "º¾½º¸ ¿¾º°·°½."}
            else:
                return {"status": "error", "message": "µ ´°»¾ ½°¹¸ ¾º½¾ °±¾µ³¾ ¾»°"}
        
        except Exception as e:
            self.logger.error(f"¸±º° ¿¾º°·° ¸º¾½¾º: {e}")
            return {"status": "error", "message": str(e)}

    def toggle_icons(self) -> Dict:
        """µµº»¸ ²¸´¸¼¾ ¸º¾½¾º."""
        if self.icons_hidden:
            return self.show_icons()
        else:
            return self.hide_icons()

    def is_hidden(self) -> bool:
        """¾²µ¸, º »¸ ¸º¾½º¸."""
        return self.icons_hidden

    def hide_taskbar(self) -> Dict:
        """¡º ¿°½µ» ·°´°."""
        try:
            taskbar = win32gui.FindWindow("Shell_traywnd", None)
            if taskbar:
                win32gui.ShowWindow(taskbar, win32con.SW_HIDE)
                self.logger.info("°½µ» ·°´° º°")
                return {"status": "ok", "message": "°½µ» ·°´° º°."}
            return {"status": "error", "message": "°½µ» ·°´° ½µ ½°¹´µ½°"}
        except Exception as e:
            self.logger.error(f"¸±º° º¸ ¿°½µ»¸ ·°´°: {e}")
            return {"status": "error", "message": str(e)}

    def show_taskbar(self) -> Dict:
        """¾º°·° ¿°½µ» ·°´°."""
        try:
            taskbar = win32gui.FindWindow("Shell_traywnd", None)
            if taskbar:
                win32gui.ShowWindow(taskbar, win32con.SW_SHOW)
                self.logger.info("°½µ» ·°´° ¿¾º°·°½°")
                return {"status": "ok", "message": "°½µ» ·°´° ¿¾º°·°½°."}
            return {"status": "error", "message": "°½µ» ·°´° ½µ ½°¹´µ½°"}
        except Exception as e:
            self.logger.error(f"¸±º° ¿¾º°·° ¿°½µ»¸ ·°´°: {e}")
            return {"status": "error", "message": str(e)}

    def enable_clean_mode(self) -> Dict:
        """º»¸ µ¶¸¼ ¸¾³¾ °±¾µ³¾ ¾»°."""
        result1 = self.hide_icons()
        result2 = self.hide_taskbar()
        
        if result1["status"] == "ok" and result2["status"] == "ok":
            return {"status": "ok", "message": " µ¶¸¼ ¸¾³¾ °±¾µ³¾ ¾»° ²º»µ½. ¿¾»·¹µ JARVIS ´» ¿°²»µ½¸."}
        else:
            return {"status": "partial", "message": "§°¸½¾ ²º»µ½¾", "icons": result1, "taskbar": result2}

    def disable_clean_mode(self) -> Dict:
        """º»¸ µ¶¸¼ ¸¾³¾ °±¾µ³¾ ¾»°."""
        result1 = self.show_icons()
        result2 = self.show_taskbar()
        
        if result1["status"] == "ok" and result2["status"] == "ok":
            return {"status": "ok", "message": " µ¶¸¼ ¸¾³¾ °±¾µ³¾ ¾»° ¾º»µ½."}
        else:
            return {"status": "partial", "message": "§°¸½¾ ¾º»µ½¾", "icons": result1, "taskbar": result2}
