"""
Windows Toast ²µ´¾¼»µ½¸
"""

from typing import Dict, Optional
import logging


class ToastNotifications:
    """°¸²½µ Windows ²µ´¾¼»µ½¸."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.app_name = "JARVIS"

    def show_toast(self, title: str, message: str, icon: str = None) -> Dict:
        """¾º°·° toast ²µ´¾¼»µ½¸µ."""
        try:
            from win10toast import ToastNotifier
            
            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message,
                icon_path=icon,
                duration=5,
                threaded=True
            )
            
            self.logger.info(f"Toast: {title} - {message}")
            return {"status": "ok", "message": "£²µ´¾¼»µ½¸µ ¿¾º°·°½¾"}
        
        except ImportError:
            self.logger.warning("win10toast ½µ °½¾²»µ½. £°½¾²¸µ: pip install win10toast")
            return {"status": "error", "message": "win10toast ½µ °½¾²»µ½"}
        
        except Exception as e:
            self.logger.error(f"¸±º° ¿¾º°·° ²µ´¾¼»µ½¸: {e}")
            return {"status": "error", "message": str(e)}

    def show_info(self, message: str) -> Dict:
        """½¾¼°¸¾½½¾µ ²µ´¾¼»µ½¸µ."""
        return self.show_toast("JARVIS", message)

    def show_warning(self, message: str) -> Dict:
        """µ´¿µ¶´µ½¸µ."""
        return self.show_toast("JARVIS - µ´¿µ¶´µ½¸µ", message)

    def show_error(self, message: str) -> Dict:
        """¸±º°."""
        return self.show_toast("JARVIS - ¸±º°", message)

    def show_success(self, message: str) -> Dict:
        """£¿µ."""
        return self.show_toast("JARVIS - £¿µ½¾", message)
