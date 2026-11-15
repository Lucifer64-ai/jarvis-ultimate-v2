"""
Windows Toast Уведомления
"""

from typing import Dict, Optional
import logging


class ToastNotifications:
    """Всплывающие Windows уведомления."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.app_name = "JARVIS"

    def show_toast(self, title: str, message: str, icon: str = None, duration: int = 5) -> Dict:
        """Показать toast уведомление."""
        try:
            from win10toast import ToastNotifier

            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message,
                icon_path=icon,
                duration=duration,
                threaded=True
            )

            self.logger.info(f"Toast: {title} - {message}")
            return {"status": "ok", "message": "Уведомление показано"}

        except ImportError:
            self.logger.warning("win10toast не установлен. Установка: pip install win10toast")
            return {"status": "error", "message": "win10toast не установлен"}

        except Exception as e:
            self.logger.error(f"Ошибка показа уведомления: {e}")
            return {"status": "error", "message": str(e)}

    def show_info(self, message: str) -> Dict:
        """Информационное уведомление."""
        return self.show_toast("JARVIS", message)

    def show_warning(self, message: str) -> Dict:
        """Предупреждение."""
        return self.show_toast("JARVIS - Предупреждение", message)

    def show_error(self, message: str) -> Dict:
        """Ошибка."""
        return self.show_toast("JARVIS - Ошибка", message)

    def show_success(self, message: str) -> Dict:
        """Успех."""
        return self.show_toast("JARVIS - Успешно", message)
