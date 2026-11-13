"""
¢µ¹-иº¾½º° JARVIS
"""

import pystray
from PIL import Image, ImageDraw
import threading


class TrayIcon:
    """º¾½º° в иµ¼½¾¼ µµ."""

    def __init__(self, brain):
        self.brain = brain
        self.icon = None
        self._create_icon()

    def _create_icon(self):
        """¡¾·´°½иµ иº¾½ºи."""
        # ¡¾·´°½иµ ¿¾¾¹ иº¾½ºи JARVIS
        image = Image.new('RGB', (64, 64), color='#0f0f1e')
        dc = ImageDraw.Draw(image)
        
        # ³
        dc.ellipse([8, 8, 56, 56], outline='#00d4ff', width=3)
        
        # ºв° J
        dc.text((24, 18), "J", fill='#00d4ff')
        
        self.image = image

    def start(self):
        """°¿º иº¾½ºи в µµ."""
        menu = pystray.Menu(
            pystray.MenuItem("¾º°·° HUD", self._show_hud),
            pystray.MenuItem("¡º HUD", self._hide_hud),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("¡°", self._show_status),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("¾´", self._quit)
        )
        
        self.icon = pystray.Icon("jarvis", self.image, "JARVIS", menu)
        
        thread = threading.Thread(target=self.icon.run, daemon=True)
        thread.start()

    def _show_hud(self, icon, item):
        """¾º°·° HUD."""
        if hasattr(self.brain, 'hud'):
            self.brain.hud.start()

    def _hide_hud(self, icon, item):
        """¡º HUD."""
        if hasattr(self.brain, 'hud'):
            self.brain.hud.stop()

    def _show_status(self, icon, item):
        """¾º°·° °."""
        status = self.brain.get_status()
        self.brain.logger.info(f"¡°: {status}")

    def _quit(self, icon, item):
        """¾´ и· ¿и»¾¶µ½и."""
        self.brain.stop()
        icon.stop()

    def stop(self):
        """°½¾вº° иº¾½ºи."""
        if self.icon:
            self.icon.stop()
