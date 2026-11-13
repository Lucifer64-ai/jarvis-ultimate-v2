"""
3D Avatar Module - ¾»¾³°¸µº¸¹ °²°° JARVIS
 µ°³¸µ ½° ³¾»¾ ¸ º¾¼°½´ ¿¾»·¾²°µ»
"""

import sys
import math
import time
import threading
from typing import Optional, Dict
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QLinearGradient


class HolographicAvatar(QWidget):
    """¾»¾³°¸µº¸¹ 3D °²°° JARVIS."""

    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.logger = brain.logger
        
        # ¡¾¾½¸µ °²°°°
        self.state = "idle"  # idle, listening, speaking, thinking, processing
        self.voice_level = 0.0
        self.rotation_angle = 0.0
        self.pulse_phase = 0.0
        self.energy_level = 0.5
        
        # °¾¹º¸ ¾¾±°¶µ½¸
        self.width = 400
        self.height = 400
        self.position_x = 100
        self.position_y = 100
        
        # ½¸¼°¸
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)  # ~60 FPS
        
        # °¾¹º° ¾º½°
        self.setup_window()
        
        self.logger.info("¢ 3D °²°° ¸½¸¸°»¸·¸¾²°½")

    def setup_window(self):
        """°¾¹º° ¿¾·°½¾³¾ ¾º½°."""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self.setGeometry(self.position_x, self.position_y, self.width, self.height)
        
        # ¾·°½¾
        self.setWindowOpacity(0.85)

    def paintEvent(self, event):
        """¸¾²º° ³¾»¾³°¸µº¾³¾ °²°°°."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # ¦µ½ °²°°°
        center_x = self.width // 2
        center_y = self.height // 2
        
        # === ¡  £¡ (Arc Reactor ¸») ===
        
        # ½µ½µµ º¾»¾
        outer_radius = 150
        self.draw_ring(painter, center_x, center_y, outer_radius, 20, 
                      QColor(0, 200, 255, 100), self.rotation_angle)
        
        # ¡µ´½µµ º¾»¾
        middle_radius = 120
        self.draw_ring(painter, center_x, center_y, middle_radius, 15,
                      QColor(0, 255, 255, 150), -self.rotation_angle * 1.5)
        
        # ½µ½½µµ º¾»¾
        inner_radius = 90
        self.draw_ring(painter, center_x, center_y, inner_radius, 10,
                      QColor(100, 255, 255, 200), self.rotation_angle * 2)
        
        # === ¯  (¿»¸¸¹ µ½) ===
        
        # »°¸ ´°
        pulse_size = 60 + math.sin(self.pulse_phase) * 10
        
        # °´¸µ½ ´°
        gradient = QRadialGradient(center_x, center_y, pulse_size)
        gradient.setColorAt(0, QColor(255, 255, 255, 255))
        gradient.setColorAt(0.3, QColor(100, 255, 255, 200))
        gradient.setColorAt(0.7, QColor(0, 200, 255, 150))
        gradient.setColorAt(1, QColor(0, 100, 200, 0))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - pulse_size, center_y - pulse_size,
                           pulse_size * 2, pulse_size * 2)
        
        # === ­ ¢§¡  ===
        
        self.draw_energy_lines(painter, center_x, center_y, inner_radius, outer_radius)
        
        # === ¢  ¡ ===
        
        if self.voice_level > 0.1:
            self.draw_voice_indicator(painter, center_x, center_y, outer_radius + 30)
        
        # === ¢¡¢ ¡¡¢¯¯ ===
        
        self.draw_state_text(painter, center_x, self.height - 50)
        
        painter.end()

    def draw_ring(self, painter: QPainter, cx: int, cy: int, radius: int, 
                  thickness: int, color: QColor, rotation: float):
        """¸¾²º° ²°°µ³¾ º¾»°."""
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(rotation)
        
        # ¡µ³¼µ½ º¾»°
        segments = 12
        for i in range(segments):
            angle = i * (360 / segments)
            painter.save()
            painter.rotate(angle)
            
            # °´¸µ½ µ³¼µ½°
            gradient = QLinearGradient(0, -radius, 0, -radius + thickness)
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            
            #  ¸µ¼ µ³¼µ½
            painter.drawRoundedRect(-thickness // 2, -radius, thickness, thickness, 3, 3)
            
            painter.restore()
        
        painter.restore()

    def draw_energy_lines(self, painter: QPainter, cx: int, cy: int, 
                          inner_r: int, outer_r: int):
        """¸¾²º° ½µ³µ¸µº¸ »¸½¸¹."""
        lines = 8
        for i in range(lines):
            angle = i * (360 / lines) + self.rotation_angle * 3
            rad = math.radians(angle)
            
            x1 = cx + math.cos(rad) * inner_r
            y1 = cy + math.sin(rad) * inner_r
            x2 = cx + math.cos(rad) * outer_r
            y2 = cy + math.sin(rad) * outer_r
            
            # °´¸µ½ »¸½¸¸
            gradient = QLinearGradient(x1, y1, x2, y2)
            gradient.setColorAt(0, QColor(0, 255, 255, 200))
            gradient.setColorAt(1, QColor(0, 255, 255, 0))
            
            pen = QPen(QBrush(gradient), 2)
            painter.setPen(pen)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def draw_voice_indicator(self, painter: QPainter, cx: int, cy: int, radius: int):
        """¸¾²º° ¸½´¸º°¾° ³¾»¾°."""
        # ¾»½ ³¾»¾°
        waves = 3
        for i in range(waves):
            wave_radius = radius + i * 15
            alpha = int(200 * (1 - i / waves) * self.voice_level)
            
            pen = QPen(QColor(0, 255, 255, alpha))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            painter.drawEllipse(cx - wave_radius, cy - wave_radius,
                               wave_radius * 2, wave_radius * 2)

    def draw_state_text(self, painter: QPainter, x: int, y: int):
        """¸¾²º° µº° ¾¾½¸."""
        state_texts = {
            "idle": "¢",
            "listening": "¡£¨®...",
            "speaking": " ®...",
            "thinking": "£®...",
            "processing": " ¢..."
        }
        
        text = state_texts.get(self.state, "¢")
        
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        
        # ¢µ½ µº°
        painter.setPen(QColor(0, 0, 0, 150))
        painter.drawText(x + 1, y + 1, text)
        
        # ½¾²½¾¹ µº
        painter.setPen(QColor(0, 255, 255, 255))
        painter.drawText(x, y, text)

    def update_animation(self):
        """±½¾²»µ½¸µ °½¸¼°¸¸."""
        # °µ½¸µ
        self.rotation_angle += 1.0
        if self.rotation_angle >= 360:
            self.rotation_angle = 0
        
        # »°¸
        self.pulse_phase += 0.1
        if self.pulse_phase >= 2 * math.pi:
            self.pulse_phase = 0
        
        # °°½¸µ ³¾»¾°
        if self.voice_level > 0:
            self.voice_level -= 0.05
            if self.voice_level < 0:
                self.voice_level = 0
        
        # µµ¸¾²º°
        self.update()

    # === £§« ¢« ===

    def set_state(self, state: str):
        """£°½¾²º° ¾¾½¸ °²°°°."""
        if state in ["idle", "listening", "speaking", "thinking", "processing"]:
            self.state = state
            self.logger.debug(f"²°°: ¾¾½¸µ -> {state}")

    def set_voice_level(self, level: float):
        """£°½¾²º° ¾²½ ³¾»¾° (0.0 - 1.0)."""
        self.voice_level = max(0.0, min(1.0, level))

    def set_energy_level(self, level: float):
        """£°½¾²º° ¾²½ ½µ³¸¸ (0.0 - 1.0)."""
        self.energy_level = max(0.0, min(1.0, level))

    def show_avatar(self):
        """¾º°·° °²°°."""
        self.show()
        self.logger.info("²°° ¿¾º°·°½")

    def hide_avatar(self):
        """¡º °²°°."""
        self.hide()
        self.logger.info("²°° º")

    def move_to_position(self, x: int, y: int):
        """µµ¼µµ½¸µ °²°°°."""
        self.position_x = x
        self.position_y = y
        self.move(x, y)

    def resize_avatar(self, width: int, height: int):
        """·¼µ½µ½¸µ °·¼µ° °²°°°."""
        self.width = width
        self.height = height
        self.setFixedSize(width, height)


class AvatarManager:
    """µ½µ´¶µ ¿°²»µ½¸ 3D °²°°¾¼."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.avatar: Optional[HolographicAvatar] = None
        self.app: Optional[QApplication] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False

    def initialize(self):
        """½¸¸°»¸·°¸ °²°°° ² ¾´µ»½¾¼ ¿¾¾ºµ."""
        if self.running:
            self.logger.warning("²°° ¶µ ·°¿µ½")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_avatar_thread, daemon=True)
        self.thread.start()
        
        # ¶¸´°½¸µ ¸½¸¸°»¸·°¸¸
        time.sleep(0.5)
        
        self.logger.info("¢ µ½µ´¶µ °²°°° ·°¿µ½")

    def _run_avatar_thread(self):
        """¾¾º ´» ·°¿º° Qt ¿¸»¾¶µ½¸."""
        try:
            self.app = QApplication(sys.argv)
            self.avatar = HolographicAvatar(self.brain)
            self.app.exec_()
        except Exception as e:
            self.logger.error(f"¸±º° ² ¿¾¾ºµ °²°°°: {e}")
        finally:
            self.running = False

    def show(self):
        """¾º°·° °²°°."""
        if self.avatar:
            self.avatar.show_avatar()
            return {"status": "ok", "message": "²°° ¿¾º°·°½"}
        return {"status": "error", "message": "²°° ½µ ¸½¸¸°»¸·¸¾²°½"}

    def hide(self):
        """¡º °²°°."""
        if self.avatar:
            self.avatar.hide_avatar()
            return {"status": "ok", "message": "²°° º"}
        return {"status": "error", "message": "²°° ½µ ¸½¸¸°»¸·¸¾²°½"}

    def set_state(self, state: str):
        """£°½¾²¸ ¾¾½¸µ °²°°°."""
        if self.avatar:
            self.avatar.set_state(state)

    def set_voice_level(self, level: float):
        """£°½¾²¸ ¾²µ½ ³¾»¾°."""
        if self.avatar:
            self.avatar.set_voice_level(level)

    def move(self, x: int, y: int):
        """µµ¼µ¸ °²°°."""
        if self.avatar:
            self.avatar.move_to_position(x, y)
            return {"status": "ok", "message": f"²°° ¿µµ¼µ½ ² ({x}, {y})"}
        return {"status": "error", "message": "²°° ½µ ¸½¸¸°»¸·¸¾²°½"}

    def resize(self, width: int, height: int):
        """·¼µ½¸ °·¼µ °²°°°."""
        if self.avatar:
            self.avatar.resize_avatar(width, height)
            return {"status": "ok", "message": f" °·¼µ ¸·¼µ½½ ½° {width}x{height}"}
        return {"status": "error", "message": "²°° ½µ ¸½¸¸°»¸·¸¾²°½"}

    def get_status(self) -> Dict:
        """¾»¸ ° °²°°°."""
        if self.avatar:
            return {
                "status": "ok",
                "running": self.running,
                "state": self.avatar.state,
                "voice_level": self.avatar.voice_level,
                "energy_level": self.avatar.energy_level,
                "position": (self.avatar.position_x, self.avatar.position_y),
                "size": (self.avatar.width, self.avatar.height)
            }
        return {"status": "error", "message": "²°° ½µ ¸½¸¸°»¸·¸¾²°½"}

    def stop(self):
        """°½¾²º° °²°°°."""
        if self.app:
            self.app.quit()
        self.running = False
        self.logger.info("²°° ¾°½¾²»µ½")
