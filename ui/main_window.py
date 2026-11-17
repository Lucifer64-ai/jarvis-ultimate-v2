"""
JARVIS Ultimate - Главное окно интерфейса
Живой интерфейс с анимациями в стиле Iron Man / J.A.R.V.I.S
"""

import sys
import time
import math
import threading
from datetime import datetime
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QRadialGradient, QLinearGradient,
    QConicalGradient, QPainterPath, QIcon, QPalette
)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ArcReactorWidget(QWidget):
    """Дуговой реактор JARVIS - центральный анимированный элемент."""

    status_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 240)
        self.rotation = 0
        self.pulse = 0
        self.status = "IDLE"
        self.voice_active = False

        # Анимационный таймер
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(40)

    def _animate(self):
        self.rotation = (self.rotation + 3) % 360
        self.pulse = (self.pulse + 2) % 100
        self.update()

    def set_status(self, status: str):
        self.status = status
        self.status_changed.emit(status)
        self.update()

    def set_voice_active(self, active: bool):
        self.voice_active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 2 - 15

        pulse = math.sin(self.pulse * 0.1) * 0.3 + 0.7

        # Внешнее свечение (дыхание)
        glow = QRadialGradient(center_x, center_y, radius * 1.4)
        glow.setColorAt(0, QColor(0, 255, 255, int(60 * pulse)))
        glow.setColorAt(0.5, QColor(0, 150, 255, int(30 * pulse)))
        glow.setColorAt(1, QColor(0, 100, 200, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - radius * 1.4, center_y - radius * 1.4,
                            radius * 2.8, radius * 2.8)

        # Внешнее кольцо
        pen = QPen(QColor(0, 255, 255, 180))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Вращающиеся сегменты
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation)

        for i in range(8):
            angle = math.radians(i * 45)
            seg_color = QColor(0, 255, 255, 100 if i % 2 == 0 else 40)
            painter.setPen(QPen(seg_color, 4))
            painter.drawLine(
                int(radius * 0.7 * math.cos(angle)),
                int(radius * 0.7 * math.sin(angle)),
                int(radius * 0.9 * math.cos(angle)),
                int(radius * 0.9 * math.sin(angle))
            )
        painter.restore()

        # Среднее кольцо (пунктир, вращается в обратную сторону)
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(-self.rotation * 1.3)

        pen = QPen(QColor(0, 191, 255, 120))
        pen.setWidth(2)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawEllipse(-radius * 0.6, -radius * 0.6, radius * 1.2, radius * 1.2)
        painter.restore()

        # Внутреннее свечение и центральный круг
        center_glow = QRadialGradient(center_x, center_y, radius * 0.35)
        center_glow.setColorAt(0, QColor(255, 255, 255, 220))
        center_glow.setColorAt(0.4, QColor(0, 255, 255, 150))
        center_glow.setColorAt(1, QColor(0, 191, 255, 60))

        painter.setBrush(QBrush(center_glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - radius * 0.35, center_y - radius * 0.35,
                            radius * 0.7, radius * 0.7)

        # Центральная точка
        center_pulse = QRadialGradient(center_x, center_y, radius * 0.15)
        center_pulse.setColorAt(0, QColor(255, 255, 255, 255))
        center_pulse.setColorAt(1, QColor(0, 255, 255, 100))
        painter.setBrush(QBrush(center_pulse))
        painter.drawEllipse(center_x - radius * 0.15, center_y - radius * 0.15,
                            radius * 0.3, radius * 0.3)

        # Статус текст
        painter.setPen(QPen(QColor(0, 255, 255)))
        font = QFont("Arial", 9, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.status)

        # Голосовая активность индикатор
        if self.voice_active:
            voice_glow = QRadialGradient(center_x, center_y, radius * 1.1)
            voice_glow.setColorAt(0, QColor(0, 255, 0, int(80 * pulse)))
            voice_glow.setColorAt(1, QColor(0, 255, 0, 0))
            painter.setBrush(QBrush(voice_glow))
            painter.drawEllipse(center_x - radius * 1.1, center_y - radius * 1.1,
                                radius * 2.2, radius * 2.2)


class StatusIndicator(QWidget):
    """Индикатор статуса с пульсацией."""

    def __init__(self, label: str, color: str = "#00bfff", parent=None):
        super().__init__(parent)
        self.label_text = label
        self.color = QColor(color)
        self.pulse = 0
        self.value = "OK"
        self.setFixedHeight(24)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._pulse)
        self.timer.start(50)

    def _pulse(self):
        self.pulse = (self.pulse + 1) % 100
        self.update()

    def set_value(self, value: str, color: Optional[str] = None):
        self.value = value
        if color:
            self.color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pulse = math.sin(self.pulse * 0.1) * 0.2 + 0.8

        # Точка индикатора
        dot_size = 10
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color.lighter(150), 2))
        painter.drawEllipse(8, 7, dot_size, dot_size)

        # Свет вокруг точки при активном состоянии
        if self.value and self.value not in ("OK", "IDLE"):
            glow = QRadialGradient(8 + dot_size // 2, 7 + dot_size // 2, dot_size * 2)
            glow.setColorAt(0, QColor(self.color.red(), self.color.green(), self.color.blue(), int(60 * pulse)))
            glow.setColorAt(1, QColor(self.color.red(), self.color.green(), self.color.blue(), 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(8 - dot_size, 7 - dot_size, dot_size * 5, dot_size * 5)

        # Текст метки
        painter.setPen(QPen(QColor(200, 230, 255)))
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(24, 20, self.label_text)

        # Значение
        painter.setPen(QPen(self.color))
        font_bold = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font_bold)
        painter.drawText(self.width() - 60, 20, self.value)


class CommandPanel(QWidget):
    """Панель ввода и отображения команд."""

    command_entered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 15, 30, 200);
                border: 1px solid rgb(0, 191, 255);
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Заголовок
        title = QLabel("JARVIS COMMAND CONSOLE")
        title.setStyleSheet("color: rgb(0, 255, 255); font-size: 13px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(title)

        # История команд
        self.command_history = QTextEdit()
        self.command_history.setReadOnly(True)
        self.command_history.setMaximumHeight(140)
        self.command_history.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 5, 15, 180);
                border: 1px solid rgb(0, 100, 150);
                border-radius: 4px;
                color: rgb(0, 255, 255);
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)
        self.command_history.append("> JARVIS v2.0.0 初期化完了")
        self.command_history.append("> Система готова к работе")
        self.command_history.append("> Ожидание команд...")
        layout.addWidget(self.command_history)

        # Поле ввода
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        prompt = QLabel(">")
        prompt.setStyleSheet("color: rgb(0, 255, 255); font-size: 13px; font-weight: bold;")
        input_layout.addWidget(prompt)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите команду...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 10, 25, 180);
                border: 1px solid rgb(0, 191, 255);
                border-radius: 4px;
                color: rgb(255, 255, 255);
                font-family: 'Consolas', monospace;
                font-size: 13px;
                padding: 6px;
            }
            QLineEdit:focus {
                border: 1px solid rgb(0, 255, 255);
            }
        """)
        self.input_field.returnPressed.connect(self._on_enter)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("ОТПРАВИТЬ")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb(0, 150, 255),
                    stop:1 rgb(0, 100, 200));
                color: rgb(255, 255, 255);
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgb(0, 191, 255),
                    stop:1 rgb(0, 150, 255));
            }
            QPushButton:pressed {
                background-color: rgb(0, 100, 200);
            }
        """)
        self.send_btn.clicked.connect(self._on_enter)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

    def _on_enter(self):
        text = self.input_field.text().strip()
        if text:
            self.command_entered.emit(text)
            self.input_field.clear()

    def add_command(self, command: str, response: str = ""):
        self.command_history.append(f"> {command}")
        if response:
            self.command_history.append(f"  {response}")
        # Прокрутка вниз
        scrollbar = self.command_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def add_system_message(self, message: str):
        self.command_history.append(f"  {message}")
        scrollbar = self.command_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class MetricsPanel(QWidget):
    """Панель системных метрик с реальными данными."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 15, 30, 180);
                border: 1px solid rgb(0, 191, 255);
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title = QLabel("SYSTEM METRICS")
        title.setStyleSheet("color: rgb(0, 255, 255); font-size: 13px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(title)

        self.cpu_label = self._create_metric_row("CPU", "0%")
        self.ram_label = self._create_metric_row("RAM", "0%")
        self.net_label = self._create_metric_row("NET", "0 MB/s")
        self.uptime_label = self._create_metric_row("UPTIME", "0h 0m")
        self.temp_label = self._create_metric_row("TEMP", "0°C")

        layout.addStretch()

        self._last_net = 0
        self._last_net_time = 0

    def _create_metric_row(self, name: str, value: str) -> QLabel:
        row = QHBoxLayout()
        name_label = QLabel(name)
        name_label.setStyleSheet("color: rgb(0, 191, 255); font-size: 11px; font-weight: bold;")
        name_label.setFixedWidth(50)

        value_label = QLabel(value)
        value_label.setStyleSheet("color: rgb(0, 255, 255); font-size: 12px; font-family: 'Consolas', monospace;")
        value_label.setFixedWidth(80)

        row.addWidget(name_label)
        row.addStretch()
        row.addWidget(value_label)

        container = QWidget()
        container.setLayout(row)
        self.layout().addWidget(container)

        return value_label

    def update_metrics(self):
        if not PSUTIL_AVAILABLE:
            return

        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent

            self.cpu_label.setText(f"{cpu:.1f}%")
            self.ram_label.setText(f"{ram:.1f}%")

            # Цвет в зависимости от загрузки
            cpu_color = "#00ff80" if cpu < 70 else "#ffaa00" if cpu < 90 else "#ff4444"
            ram_color = "#00ff80" if ram < 80 else "#ffaa00" if ram < 95 else "#ff4444"
            self.cpu_label.setStyleSheet(f"color: {cpu_color}; font-size: 12px; font-family: 'Consolas', monospace;")
            self.ram_label.setStyleSheet(f"color: {ram_color}; font-size: 12px; font-family: 'Consolas', monospace;")

            # Сетевая скорость
            counters = psutil.net_io_counters()
            total = counters.bytes_sent + counters.bytes_recv
            now = time.time()

            if self._last_net_time > 0:
                speed = (total - self._last_net) / (now - self._last_net_time) / (1024 * 1024)
                self.net_label.setText(f"{speed:.1f} MB/s")
            self._last_net = total
            self._last_net_time = now

            # Время работы
            boot = psutil.boot_time()
            uptime_sec = int(time.time() - boot)
            hours = uptime_sec // 3600
            minutes = (uptime_sec % 3600) // 60
            self.uptime_label.setText(f"{hours}h {minutes}m")

        except Exception:
            pass


class VoiceWaveWidget(QWidget):
    """Анимированная волна голосовой активности."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.active = False
        self.wave_phase = 0
        self.wave_x = [i * 6 for i in range(60)]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)

    def _animate(self):
        self.wave_phase = (self.wave_phase + 1) % 360
        if self.active:
            self.update()

    def set_active(self, active: bool):
        self.active = active
        if active:
            self.timer.start(40)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.active:
            # Показываем неактивное состояние
            painter.setPen(QPen(QColor(0, 100, 150, 80), 2))
            for i in range(0, self.width(), 8):
                painter.drawLine(i, self.height() // 2 - 5, i, self.height() // 2 + 5)
            return

        center_y = self.height() // 2
        amplitude = 15 + math.sin(self.wave_phase * 0.1) * 8

        path = QPainterPath()
        for i, offset_x in enumerate(self.wave_x):
            y = center_y + math.sin(self.wave_phase * 0.15 + i * 0.3) * amplitude
            if i == 0:
                path.moveTo(offset_x, y)
            else:
                path.lineTo(offset_x, y)

        # Градиент для волны
        gradient = QLinearGradient(0, center_y - 30, 0, center_y + 30)
        gradient.setColorAt(0, QColor(0, 255, 255, 100))
        gradient.setColorAt(0.5, QColor(0, 255, 255, 220))
        gradient.setColorAt(1, QColor(0, 255, 255, 100))

        painter.setPen(QPen(QColor(0, 255, 255, 200), 3))
        painter.drawPath(path)

        # Заполнение под волной
        fill_path = QPainterPath(path)
        fill_path.lineTo(self.width(), self.height())
        fill_path.lineTo(0, self.height())
        fill_path.closeSubpath()
        painter.fillPath(fill_path, QBrush(QColor(0, 255, 255, 20)))


class MainWindow(QMainWindow):
    """Главное окно интерфейса JARVIS с живыми анимациями."""

    def __init__(self, brain=None):
        super().__init__()
        self.brain = brain

        # Настройки окна
        self.setWindowTitle("J.A.R.V.I.S - Ultimate Interface")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

        # Темный градиентный фон
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #050a14,
                    stop:0.5 #0a1526,
                    stop:1 #050a14);
            }
        """)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # === Левая панель: статус и метрики ===
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        # Статус индикаторы
        status_group = QVBoxLayout()
        status_title = QLabel("СИСТЕМНЫЙ СТАТУС")
        status_title.setStyleSheet("color: #00bfff; font-size: 12px; font-weight: bold; letter-spacing: 2px;")
        status_group.addWidget(status_title)

        self.cpu_ind = StatusIndicator("Процессор", "#00bfff")
        self.ram_ind = StatusIndicator("Память", "#00bfff")
        self.net_ind = StatusIndicator("Сеть", "#00bfff")
        self.voice_ind = StatusIndicator("Голос", "#00bfff")
        self.ai_ind = StatusIndicator("AI Core", "#00bfff")

        status_group.addWidget(self.cpu_ind)
        status_group.addWidget(self.ram_ind)
        status_group.addWidget(self.net_ind)
        status_group.addWidget(self.voice_ind)
        status_group.addWidget(self.ai_ind)
        left_panel.addLayout(status_group)

        # Метрики панель
        self.metrics_panel = MetricsPanel()
        left_panel.addWidget(self.metrics_panel)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.btn_wake = QPushButton("ПРОБУДИТЬ")
        self.btn_sleep = QPushButton("СНЯТЬ СО СНА")
        self.btn_settings = QPushButton("НАСТРОЙКИ")

        for btn in (self.btn_wake, self.btn_sleep, self.btn_settings):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 150, 255, 120);
                    border: 1px solid rgb(0, 191, 255);
                    border-radius: 4px;
                    color: rgb(255, 255, 255);
                    font-weight: bold;
                    font-size: 11px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 200, 255, 180);
                }
            """)

        btn_layout.addWidget(self.btn_wake)
        btn_layout.addWidget(self.btn_sleep)
        btn_layout.addWidget(self.btn_settings)
        left_panel.addLayout(btn_layout)

        left_panel.addStretch()
        main_layout.addLayout(left_panel, stretch=1)

        # === Центр: Арк-реактор и заголовок ===
        center_panel = QVBoxLayout()
        center_panel.setSpacing(10)

        # Арк-реактор
        self.arc_reactor = ArcReactorWidget()
        center_panel.addWidget(self.arc_reactor, alignment=Qt.AlignCenter)

        # Название
        title = QLabel("J.A.R.V.I.S")
        title.setStyleSheet("color: #00ffff; font-size: 40px; font-weight: bold; letter-spacing: 8px;")
        title.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(title)

        subtitle = QLabel("Just A Rather Very Intelligent System")
        subtitle.setStyleSheet("color: #00bfff; font-size: 13px; letter-spacing: 3px;")
        subtitle.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(subtitle)

        # Статус строка
        self.status_label = QLabel("СИСТЕМА ГОТОВА")
        self.status_label.setStyleSheet("color: #00ff80; font-size: 12px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(self.status_label)

        # Голосовая волна
        self.voice_wave = VoiceWaveWidget()
        center_panel.addWidget(self.voice_wave, alignment=Qt.AlignCenter)

        main_layout.addLayout(center_panel, stretch=2)

        # === Правая панель: часы, дата, консоль ===
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        # Часы
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #00ffff; font-size: 56px; font-weight: bold; font-family: 'Consolas', monospace;")
        self.time_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.time_label)

        self.date_label = QLabel()
        self.date_label.setStyleSheet("color: #00bfff; font-size: 16px; font-weight: bold;")
        self.date_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.date_label)

        right_panel.addSpacing(10)

        # Информация о системе
        info_group = QVBoxLayout()
        info_title = QLabel("ИНФОРМАЦИЯ")
        info_title.setStyleSheet("color: #00bfff; font-size: 12px; font-weight: bold; letter-spacing: 2px;")
        info_group.addWidget(info_title)

        self.info_hostname = QLabel("Хост: -")
        self.info_hostname.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.info_ip = QLabel("IP: -")
        self.info_ip.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.info_proc = QLabel("Процессы: -")
        self.info_proc.setStyleSheet("color: #ffffff; font-size: 12px;")

        info_group.addWidget(self.info_hostname)
        info_group.addWidget(self.info_ip)
        info_group.addWidget(self.info_proc)
        info_group.addStretch()
        right_panel.addLayout(info_group)

        right_panel.addSpacing(10)

        # Консоль команд
        self.command_panel = CommandPanel()
        self.command_panel.command_entered.connect(self._on_command)
        right_panel.addWidget(self.command_panel, stretch=1)

        main_layout.addLayout(right_panel, stretch=1)

        # === Таймеры ===
        # Часы
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

        # Системные метрики
        self.metrics_timer = QTimer(self)
        self.metrics_timer.timeout.connect(self._update_metrics)
        self.metrics_timer.start(1000)

        # Подключение к мозгу
        if self.brain:
            self._connect_brain()

        # Приветственное сообщение
        QTimer.singleShot(500, lambda: self.command_panel.add_system_message("JARVIS интерфейс активирован"))
        QTimer.singleShot(800, lambda: self.command_panel.add_system_message("Все модули загружены"))
        QTimer.singleShot(1200, lambda: self.set_status("ГОТОВ К РАБОТЕ"))

    def _connect_brain(self):
        """Подключение сигналов мозга к интерфейсу."""
        try:
            self.arc_reactor.status_changed.connect(self.status_label.setText)

            if hasattr(self.brain, 'process_command'):
                pass  # Команда будет обработана через _on_command

            if hasattr(self.brain, 'voice_recognizer') and self.brain.voice_recognizer:
                # Голосовой детектор
                pass
        except Exception:
            pass

    def _update_clock(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%d %B %Y, %A"))

    def _update_metrics(self):
        self.metrics_panel.update_metrics()

        if PSUTIL_AVAILABLE:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent

                self.cpu_ind.set_value(f"{cpu:.1f}%", "#00ff80" if cpu < 70 else "#ffaa00")
                self.ram_ind.set_value(f"{ram:.1f}%", "#00ff80" if ram < 80 else "#ffaa00")

                # Информация о системе
                import socket
                hostname = socket.gethostname()
                self.info_hostname.setText(f"Хост: {hostname}")

                boot = psutil.boot_time()
                uptime_sec = int(time.time() - boot)
                hours = uptime_sec // 3600
                minutes = (uptime_sec % 3600) // 60
                self.uptime_label.setText(f"{hours}h {minutes}m")

                proc_count = len(psutil.pids())
                self.info_proc.setText(f"Процессы: {proc_count}")
            except Exception:
                pass

    def _on_command(self, command: str):
        """Обработка команды из консоли."""
        self.command_panel.add_command(command, "Обработка...")
        self.set_status("ОБРАБОТКА")

        if self.brain and hasattr(self.brain, 'process_command'):
            try:
                result = self.brain.process_command(command)
                response = result.get('message', str(result)) if isinstance(result, dict) else str(result)
                self.command_panel.add_command("", response)
                self.set_status("ГОТОВ")
            except Exception as e:
                self.command_panel.add_command("", f"Ошибка: {e}")
                self.set_status("ОШИБКА")

    def set_status(self, status: str):
        self.status_label.setText(status)
        self.arc_reactor.set_status(status)
        color = "#00ff80" if status in ("ГОТОВ К РАБОТЕ", "ГОТОВ") else "#ffaa00" if status == "ОБРАБОТКА" else "#ff4444"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")

    def set_voice_active(self, active: bool):
        self.voice_wave.set_active(active)
        self.arc_reactor.set_voice_active(active)
        self.voice_ind.set_value("LISTENING" if active else "IDLE",
                                 "#00ff80" if active else "#00bfff")

    def closeEvent(self, event):
        # Не закрывать полностью, а свернуть в трей (опционально)
        event.accept()


def run_interface(brain=None):
    """Запуск графического интерфейса JARVIS."""
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS Ultimate")
    app.setApplicationVersion("2.0.0")

    font = QFont("Arial", 10)
    app.setFont(font)

    window = MainWindow(brain)
    window.show()

    return app.exec_()


if __name__ == "__main__":
    run_interface()
