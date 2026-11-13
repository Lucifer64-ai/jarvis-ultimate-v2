"""
¡иµ¼° вµ´¾¼»µ½и¹ JARVIS
"""

from plyer import notification
from typing import Optional
import threading


class NotificationManager:
    """£¿°в»µ½иµ вµ´¾¼»µ½и¼и."""

    def __init__(self, brain):
        self.brain = brain

    def show(self, title: str, message: str, timeout: int = 10):
        """¾º°·° вµ´¾¼»µ½иµ."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="JARVIS",
                timeout=timeout
            )
        except Exception as e:
            self.brain.logger.error(f"и±º° ¿¾º°·° вµ´¾¼»µ½и: {e}")

    def show_async(self, title: str, message: str, timeout: int = 10):
        """¾º°·° вµ´¾¼»µ½иµ °и½¾½½¾."""
        thread = threading.Thread(
            target=self.show,
            args=(title, message, timeout),
            daemon=True
        )
        thread.start()

    def alert(self, message: str, level: str = "info"):
        """¾º°·° ¿µ´¿µ¶´µ½иµ."""
        icons = {
            "info": "¢¹¯и",
            "warning": "¢ ¯и",
            "error": "¢",
            "success": "¢"
        }
        icon = icons.get(level, "¢¹¯и")
        self.show(f"{icon} JARVIS", message)
