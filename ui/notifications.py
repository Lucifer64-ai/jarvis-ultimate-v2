"""
¡¸µ¼° ²µ´¾¼»µ½¸¹ JARVIS
"""

from plyer import notification
from typing import Optional
import threading


class NotificationManager:
    """£¿°²»µ½¸µ ²µ´¾¼»µ½¸¼¸."""

    def __init__(self, brain):
        self.brain = brain

    def show(self, title: str, message: str, timeout: int = 10):
        """¾º°·° ²µ´¾¼»µ½¸µ."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="JARVIS",
                timeout=timeout
            )
        except Exception as e:
            self.brain.logger.error(f"¸±º° ¿¾º°·° ²µ´¾¼»µ½¸: {e}")

    def show_async(self, title: str, message: str, timeout: int = 10):
        """¾º°·° ²µ´¾¼»µ½¸µ °¸½¾½½¾."""
        thread = threading.Thread(
            target=self.show,
            args=(title, message, timeout),
            daemon=True
        )
        thread.start()

    def alert(self, message: str, level: str = "info"):
        """¾º°·° ¿µ´¿µ¶´µ½¸µ."""
        icons = {
            "info": "¢¹¯¸",
            "warning": "¢ ¯¸",
            "error": "¢",
            "success": "¢"
        }
        icon = icons.get(level, "¢¹¯¸")
        self.show(f"{icon} JARVIS", message)
