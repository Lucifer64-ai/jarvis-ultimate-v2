"""
JARVIS HUD - Голографический интерфейс в стиле Тони Старка
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
    """Центральный виджет - Arc Reactor с голографической волной."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.pulse_phase = 0
        self.voice_level = 0.0

        # Таймер анимации
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)

    def _animate(self):
        """Анимация пульсации."""
        self.pulse_phase += 0.1
        if self.pulse_phase > 6.28:
            self.pulse_phase = 0
        self.update()

    def set_voice_level(self, level: float):
        """Установить уровень голоса."""
        self.voice_level = max(0.0, min(1.0, level))
        self.update()

    def paintEvent(self, event):
        """Отрисовка Arc Reactor."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 80

        # Пульсация
        pulse = (self.pulse_phase.sin() + 1) / 2 if hasattr(self.pulse_phase, 'sin') else 0.5
        pulse_radius = radius + pulse * 10

        # Внешнее свечение
        gradient = QRadialGradient(center_x, center_y, pulse_radius)
        gradient.setColorAt(0, QColor(0, 200, 255, 100))
        gradient.setColorAt(0.5, QColor(0, 150, 255, 50))
        gradient.setColorAt(1, QColor(0, 100, 255, 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - pulse_radius, center_y - pulse_radius, 
                          pulse_radius * 2, pulse_radius * 2)

        # Внутренний круг
        painter.setPen(QPen(QColor(0, 200, 255, 200), 3))
        painter.setBrush(QBrush(QColor(0, 50, 100, 100)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Голографическая волна
        if self.voice_level > 0:
            wave_height = self.voice_level * 30
            painter.setPen(QPen(QColor(0, 255, 255, 200), 2))

            for i in range(5):
                offset = i * 10 - 20
                amplitude = wave_height * (1 - abs(offset) / 30)
                painter.drawLine(center_x + offset - 5, center_y - amplitude,
                               center_x + offset + 5, center_y + amplitude)


class SystemPanel(QWidget):
    """Панель с системной информацией."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 20, 40, 150);
                border: 2px solid rgba(0, 200, 255, 100);
                border-radius: 10px;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 200, 255, 100))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            color: rgb(0, 200, 255);
            font-size: 14px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.title_label)

        # Контент
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

    def add_stat(self, label: str, value: str = ""):
        """Добавить статистику."""
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
    """Главное окно JARVIS HUD."""

    voice_level_signal = pyqtSignal(float)

    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.logger = brain.logger

        # Настройки окна
        self.setWindowTitle("JARVIS HUD")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Размер и позиция
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Верхний ряд панелей
        top_layout = QHBoxLayout()

        # Левая верхняя панель - Время и дата
        self.time_panel = SystemPanel("ВРЕМЯ")
        self.time_label = self.time_panel.add_stat("Время", "--:--")
        self.date_label = self.time_panel.add_stat("Дата", "--.--.----")
        top_layout.addWidget(self.time_panel)

        top_layout.addStretch()

        # Правая верхняя панель - Система
        self.system_panel = SystemPanel("СИСТЕМА")
        self.cpu_label = self.system_panel.add_stat("CPU", "0%")
        self.ram_label = self.system_panel.add_stat("RAM", "0%")
        self.disk_label = self.system_panel.add_stat("Диск", "0%")
        top_layout.addWidget(self.system_panel)

        main_layout.addLayout(top_layout)

        # Центр - Arc Reactor
        center_layout = QHBoxLayout()
        center_layout.addStretch()

        self.arc_reactor = ArcReactorWidget()
        center_layout.addWidget(self.arc_reactor)

        center_layout.addStretch()
        main_layout.addLayout(center_layout)

        # Нижний ряд панелей
        bottom_layout = QHBoxLayout()

        # Левая нижняя панель - Команды
        self.command_panel = SystemPanel("КОМАНДА")
        self.command_label = self.command_panel.add_stat("Последняя", "Нет данных")
        bottom_layout.addWidget(self.command_panel)

        bottom_layout.addStretch()

        # Правая нижняя панель - Сеть
        self.network_panel = SystemPanel("СЕТЬ")
        self.network_label = self.network_panel.add_stat("Статус", "Подключено")
        self.speed_label = self.network_panel.add_stat("Скорость", "0 MB/s")
        bottom_layout.addWidget(self.network_panel)

        main_layout.addLayout(bottom_layout)

        # Таймер обновления данных
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_data)
        self.update_timer.start(1000)

        # Подключение сигнала голоса
        self.voice_level_signal.connect(self.arc_reactor.set_voice_level)

        self.logger.info("JARVIS HUD инициализирован")

    def _update_data(self):
        """Обновление системных данных."""
        from datetime import datetime

        # Время и дата
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%d.%m.%Y"))

        # Система
        self.cpu_label.setText(f"{psutil.cpu_percent()}%")
        self.ram_label.setText(f"{psutil.virtual_memory().percent}%")
        self.disk_label.setText(f"{psutil.disk_usage('/').percent}%")

        # Сеть
        try:
            net_io = psutil.net_io_counters()
            speed_mb = (net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024
            self.speed_label.setText(f"{speed_mb:.1f} MB/s")
        except:
            self.speed_label.setText("N/A")

    def update_command(self, command: str):
        """Обновить поле последней команды."""
        self.command_label.setText(command[:30] + "..." if len(command) > 30 else command)

    def set_voice_level(self, level: float):
        """Установить уровень голоса."""
        self.voice_level_signal.emit(level)

    def show_hud(self):
        """Показать HUD."""
        self.show()
        self.logger.info("JARVIS HUD показан")

    def hide_hud(self):
        """Скрыть HUD."""
        self.hide()
        self.logger.info("JARVIS HUD скрыт")

    def toggle_hud(self):
        """Переключить видимость HUD."""
        if self.isVisible():
            self.hide_hud()
        else:
            self.show_hud()
