"""
Система уведомлений JARVIS
"""

from plyer import notification
from typing import Optional
import threading


class NotificationManager:
    """Управление всплывающими уведомлениями."""

    def __init__(self, brain):
        self.brain = brain

    def show(self, title: str, message: str, timeout: int = 10):
        """Показать уведомление."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="JARVIS",
                timeout=timeout
            )
        except Exception as e:
            self.brain.logger.error(f"Ошибка показа уведомления: {e}")

    def show_async(self, title: str, message: str, timeout: int = 10):
        """Показать уведомление асинхронно."""
        thread = threading.Thread(
            target=self.show,
            args=(title, message, timeout),
            daemon=True
        )
        thread.start()

    def alert(self, message: str, level: str = "info"):
        """Показать предупреждение."""
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }
        icon = icons.get(level, "ℹ️")
        self.show(f"{icon} JARVIS", message)
