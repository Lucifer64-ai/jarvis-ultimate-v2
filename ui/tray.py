"""
Трей-иконка JARVIS
"""

import pystray
from PIL import Image, ImageDraw
import threading


class TrayIcon:
    """Иконка в системном трее."""

    def __init__(self, brain):
        self.brain = brain
        self.icon = None
        self._create_icon()

    def _create_icon(self):
        """Создание простой иконки."""
        # Создание простой иконки JARVIS
        image = Image.new('RGB', (64, 64), color='#0f0f1e')
        dc = ImageDraw.Draw(image)

        # Круг
        dc.ellipse([8, 8, 56, 56], outline='#00d4ff', width=3)

        # Буква J
        dc.text((24, 18), "J", fill='#00d4ff')

        self.image = image

    def start(self):
        """Запуск иконки в трее."""
        menu = pystray.Menu(
            pystray.MenuItem("Показать HUD", self._show_hud),
            pystray.MenuItem("Скрыть HUD", self._hide_hud),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Статус", self._show_status),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Выход", self._quit)
        )

        self.icon = pystray.Icon("jarvis", self.image, "JARVIS", menu)

        thread = threading.Thread(target=self.icon.run, daemon=True)
        thread.start()

    def _show_hud(self, icon, item):
        """Показать HUD."""
        if hasattr(self.brain, 'hud'):
            self.brain.hud.start()

    def _hide_hud(self, icon, item):
        """Скрыть HUD."""
        if hasattr(self.brain, 'hud'):
            self.brain.hud.stop()

    def _show_status(self, icon, item):
        """Показать статус."""
        status = self.brain.get_status()
        self.brain.logger.info(f"Статус: {status}")

    def _quit(self, icon, item):
        """Выход из приложения."""
        self.brain.stop()
        icon.stop()

    def stop(self):
        """Остановка иконки."""
        if self.icon:
            self.icon.stop()
