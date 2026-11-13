"""
JARVIS HUD - ¾»¾³°¸µº¸¹ ¸½µµ¹ ² ¸»µ ¢¾½¸ ¡°º°
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QBrush, QRadialGradient
import psutil
import threading


class ArcReactorWidget(QWidget):
    """¦µ½°»½¹ ²¸´¶µ - Arc Reactor  ³¾»¾¾²¾¹ ²¾»½¾¹."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.pulse_phase = 0
        self.voice_level = 0.0
        
        # ¢°¹¼µ °½¸¼°¸¸
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)
    
    def _animate(self):
        """½¸¼°¸ ¿»°¸¸."""
        self.pulse_phase += 0.1
        if self.pulse_phase > 6.28:
            self.pulse_phase = 0
        self.update()
    
    def set_voice_level(self, level: float):
        """£°½¾²¸ ¾²µ½ ³¾»¾°."""
        self.voice_level = max(0.0, min(1.0, level))
        self.update()
    
    def paintEvent(self, event):
        """¸¾²º° Arc Reactor."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 80
        
        # »°¸
        pulse = (self.pulse_phase.sin() + 1) / 2 if hasattr(self.pulse_phase, 'sin') else 0.5
        pulse_radius = radius + pulse * 10
        
        # ниниµ ²µµ½¸µ
        gradient = QRadialGradient(center_x, center_y, pulse_radius)
        gradient.setColorAt(0, QColor(0, 200, 255, 100))
        gradient.setColorAt(0.5, QColor(0, 150, 255, 50))
        gradient.setColorAt(1, QColor(0, 100, 255, 0))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - pulse_radius, center_y - pulse_radius, 
                          pulse_radius * 2, pulse_radius * 2)
        
        # ½µ½½¸¹ º³
        painter.setPen(QPen(QColor(0, 200, 255, 200), 3))
        painter.setBrush(QBrush(QColor(0, 50, 100, 100)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # ¾»¾¾²° ²¾»на
        if self.voice_level > 0:
            wave_height = self.voice_level * 30
            painter.setPen(QPen(QColor(0, 255, 255, 200), 2))
            
            for i in range(5):
                offset = i * 10 - 20
                amplitude = wave_height * (1 - abs(offset) / 30)
                painter.drawLine(center_x + offset - 5, center_y - amplitude,
                               center_x + offset + 5, center_y + amplitude)


class SystemPanel(QWidget):
    """°ни»  ¸µ¼½¾¹ ¸½¾¼°¸µ¹."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 20, 40, 150);
                border: 2px solid rgba(0, 200, 255, 100);
                border-radius: 10px;
            }
        """)
        
        # ¢µ½
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 200, 255, 100))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # °³¾»¾²¾º
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            color: rgb(0, 200, 255);
            font-size: 14px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.title_label)
        
        # ¾½µ½
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
    
    def add_stat(self, label: str, value: str = ""):
        """¾±°²¸ °¸¸º."""
        row = QHBoxLayout()
        
        name_label = QLabel(label)
        name_label.setStyleSheet("""
            color: rgb(150, 200, 255);
            font-size: 12px;
            background: transparent;
            border: none;
        """)
        row.addWidget(name_label)
        
        row.addStretch()
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            color: rgb(0, 255, 255);
            font-size: 12px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        row.addWidget(value_label)
        
        self.content_layout.addLayout(row)
        return value_label


class JarvisHUD(QMainWindow):
    """»°²½¾µ ¾º½¾ JARVIS HUD."""
    
    voice_level_signal = pyqtSignal(float)
    
    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.logger = brain.logger
        
        # °¾¹º¸ ¾ºна
        self.setWindowTitle("JARVIS HUD")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        #  °·¼µ ¸ ¿¾·¸¸
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # ¦µ½°»½¹ ²¸´¶µ
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # µ½ ¿°ни»
        top_layout = QHBoxLayout()
        
        # µ²° ²µ½ - µ¼ ¸ ´°°
        self.time_panel = SystemPanel(" ¯")
        self.time_label = self.time_panel.add_stat("µ¼", "--:--")
        self.date_label = self.time_panel.add_stat("°°", "--.--.----")
        top_layout.addWidget(self.time_panel)
        
        top_layout.addStretch()
        
        # °²° ²µ½ - ¡¸µ¼°
        self.system_panel = SystemPanel("¡¡¢")
        self.cpu_label = self.system_panel.add_stat("CPU", "0%")
        self.ram_label = self.system_panel.add_stat("RAM", "0%")
        self.disk_label = self.system_panel.add_stat("¸º", "0%")
        top_layout.addWidget(self.system_panel)
        
        main_layout.addLayout(top_layout)
        
        # ¦µ½ - Arc Reactor
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        
        self.arc_reactor = ArcReactorWidget()
        center_layout.addWidget(self.arc_reactor)
        
        center_layout.addStretch()
        main_layout.addLayout(center_layout)
        
        # ¸¶½ ¿°ни»
        bottom_layout = QHBoxLayout()
        
        # µ²° ½¸¶½ - ¾¼°½´
        self.command_panel = SystemPanel("«")
        self.command_label = self.command_panel.add_stat("¾»µ´½", "µ ´°½½")
        bottom_layout.addWidget(self.command_panel)
        
        bottom_layout.addStretch()
        
        # °²° ½¸¶½ - ¡µ
        self.network_panel = SystemPanel("¡¢¬")
        self.network_label = self.network_panel.add_stat("¡°", "¾´º»µ½¾")
        self.speed_label = self.network_panel.add_stat("¡º¾¾", "0 MB/s")
        bottom_layout.addWidget(self.network_panel)
        
        main_layout.addLayout(bottom_layout)
        
        # ¢°¹¼µ ¾±½¾²»µ½¸ ´°½½
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_data)
        self.update_timer.start(1000)
        
        # ¾´º»µ½¸µ ¸³на»° ³¾»¾°
        self.voice_level_signal.connect(self.arc_reactor.set_voice_level)
        
        self.logger.info("JARVIS HUD ¸½¸¸°»из¸¾²°½")
    
    def _update_data(self):
        """±½¾²»µ½¸µ ¸µ¼½ ´°½½."""
        from datetime import datetime
        
        # µ¼ ¸ ´°°
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%d.%m.%Y"))
        
        # ¡¸µ¼°
        self.cpu_label.setText(f"{psutil.cpu_percent()}%")
        self.ram_label.setText(f"{psutil.virtual_memory().percent}%")
        self.disk_label.setText(f"{psutil.disk_usage('/').percent}%")
        
        # ¡µ
        try:
            net_io = psutil.net_io_counters()
            speed_mb = (net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024
            self.speed_label.setText(f"{speed_mb:.1f} MB/s")
        except:
            self.speed_label.setText("N/A")
    
    def update_command(self, command: str):
        """±½¾²¸ ¿¾»µ´½ команд."""
        self.command_label.setText(command[:30] + "..." if len(command) > 30 else command)
    
    def set_voice_level(self, level: float):
        """£°½¾²¸ ¾²µ½ ³¾»¾°."""
        self.voice_level_signal.emit(level)
    
    def show_hud(self):
        """¾º°·° HUD."""
        self.show()
        self.logger.info("JARVIS HUD ¿¾º°·°½")
    
    def hide_hud(self):
        """¡º HUD."""
        self.hide()
        self.logger.info("JARVIS HUD º")
    
    def toggle_hud(self):
        """µµº»¸ ²¸´¸¼¾ HUD."""
        if self.isVisible():
            self.hide_hud()
        else:
            self.show_hud()
