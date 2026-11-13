"""
HUD-¸½µµ¹ JARVIS ² ¸»µ Iron Man
"""

import tkinter as tk
from tkinter import Canvas
import threading
import psutil
from datetime import datetime


class HUDOverlay:
    """¾»¾³°¸µº¸¹ HUD-¾²µ»µ¹."""

    def __init__(self, brain):
        self.brain = brain
        self.root = None
        self.canvas = None
        self.running = False
        self.config = brain.config.get("hud", {})

    def start(self):
        """°¿º HUD ² ¾´µ»½¾¼ ¿¾¾ºµ."""
        if not self.config.get("enabled", True):
            return
        
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        """½¾²½¾¹ ¸º» HUD."""
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.7)
        self.root.configure(bg='black')
        
        #  °·¼µ ¸ ¿¾·¸¸
        width, height = 400, 300
        screen_width = self.root.winfo_screenwidth()
        
        position = self.config.get("position", "top-right")
        if position == "top-right":
            x = screen_width - width - 20
            y = 20
        else:
            x = 20
            y = 20
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Canvas ´» ¸¾²°½¸
        self.canvas = Canvas(self.root, width=width, height=height, bg='black', highlightthickness=0)
        self.canvas.pack()
        
        #  °¼º°
        self.canvas.create_rectangle(5, 5, width-5, height-5, outline='#00d4ff', width=2)
        
        # °³¾»¾²¾º
        self.canvas.create_text(width//2, 25, text="J.A.R.V.I.S.", fill='#00d4ff', font=('Consolas', 16, 'bold'))
        
        self.running = True
        self._update()
        self.root.mainloop()

    def _update(self):
        """±½¾²»µ½¸µ ´°½½ HUD."""
        if not self.running:
            return
        
        try:
            # ¸º° ° ´°½½
            self.canvas.delete("data")
            
            # µ¼
            now = datetime.now().strftime("%H:%M:%S")
            self.canvas.create_text(200, 60, text=now, fill='#00d4ff', font=('Consolas', 14), tags="data")
            
            # CPU
            cpu = psutil.cpu_percent()
            self.canvas.create_text(50, 100, text=f"CPU: {cpu}%", fill='#00ff88', font=('Consolas', 11), anchor='w', tags="data")
            
            # RAM
            ram = psutil.virtual_memory().percent
            self.canvas.create_text(50, 130, text=f"RAM: {ram}%", fill='#00ff88', font=('Consolas', 11), anchor='w', tags="data")
            
            # Battery
            battery = psutil.sensors_battery()
            if battery:
                self.canvas.create_text(50, 160, text=f"BAT: {battery.percent}%", fill='#ffaa00', font=('Consolas', 11), anchor='w', tags="data")
            
            # ¡°
            self.canvas.create_text(200, 250, text="SYSTEM ONLINE", fill='#00d4ff', font=('Consolas', 10), tags="data")
            
        except Exception as e:
            self.brain.logger.error(f"¸±º° ¾±½¾²»µ½¸ HUD: {e}")
        
        # ±½¾²»µ½¸µ º°¶´µ 2 µº½´
        self.root.after(2000, self._update)

    def stop(self):
        """°½¾²º° HUD."""
        self.running = False
        if self.root:
            self.root.quit()

    def show_message(self, message: str, duration: int = 3000):
        """¾º°·° ²µ¼µ½½¾µ ¾¾±µ½¸µ."""
        if not self.canvas:
            return
        
        text_id = self.canvas.create_text(
            200, 200, text=message, fill='#ffffff', font=('Consolas', 12)
        )
        self.root.after(duration, lambda: self.canvas.delete(text_id))
