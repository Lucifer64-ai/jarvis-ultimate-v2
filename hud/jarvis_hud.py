"""
JARVIS HUD Interface - стиль Iron Man
Futuristic holographic display with PyQt5
"""

import sys
from typing import Dict, Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QRadialGradient, QLinearGradient


class ArcReactorWidget(QWidget):
    """Виджет дугового реактора (центральный элемент HUD)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.rotation = 0
        self.pulse = 0
        self.status = "IDLE"

        # Таймер анимации
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)

    def _animate(self):
        self.rotation = (self.rotation + 2) % 360
        self.pulse = (self.pulse + 1) % 100
        self.update()

    def set_status(self, status: str):
        self.status = status
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 2 - 10

        # Внешнее свечение
        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0, QColor(0, 191, 255, 100))
        gradient.setColorAt(0.7, QColor(0, 191, 255, 50))
        gradient.setColorAt(1, QColor(0, 191, 255, 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Вращающиеся кольца
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation)

        # Внешнее кольцо
        pen = QPen(QColor(0, 191, 255, 200))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(-radius, -radius, radius * 2, radius * 2)

        # Среднее кольцо (пунктирное)
        pen.setStyle(Qt.DashLine)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(-radius * 0.7, -radius * 0.7, radius * 1.4, radius * 1.4)

        painter.restore()

        # Внутреннее кольцо (вращается в обратную сторону)
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(-self.rotation * 1.5)

        pen = QPen(QColor(0, 255, 255, 150))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(-radius * 0.4, -radius * 0.4, radius * 0.8, radius * 0.8)

        painter.restore()

        # Центральный круг
        center_gradient = QRadialGradient(center_x, center_y, radius * 0.3)
        center_gradient.setColorAt(0, QColor(255, 255, 255, 200))
        center_gradient.setColorAt(0.5, QColor(0, 191, 255, 150))
        center_gradient.setColorAt(1, QColor(0, 191, 255, 50))

        painter.setBrush(QBrush(center_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - radius * 0.3, center_y - radius * 0.3, 
                           radius * 0.6, radius * 0.6)

        # Статус текст
        painter.setPen(QPen(QColor(0, 255, 255)))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.status)


class StatusPanel(QWidget):
    """Панель статуса системы."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 20, 40, 180); border: 1px solid rgb(0, 191, 255); border-radius: 5px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок
        title = QLabel("SYSTEM STATUS")
        title.setStyleSheet("color: rgb(0, 255, 255); font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        # Статусы
        self.status_labels = {}
        statuses = ["CPU", "RAM", "Network", "Voice", "AI"]

        for status in statuses:
            row = QHBoxLayout()
            label = QLabel(f"{status}:")
            label.setStyleSheet("color: rgb(0, 191, 255); font-size: 12px;")
            row.addWidget(label)

            value = QLabel("OK")
            value.setStyleSheet("color: rgb(0, 255, 128); font-size: 12px;")
            row.addWidget(value)

            row.addStretch()
            layout.addLayout(row)
            self.status_labels[status] = value

        layout.addStretch()

    def update_status(self, key: str, value: str, color: str = "rgb(0, 255, 128)"):
        if key in self.status_labels:
            self.status_labels[key].setText(value)
            self.status_labels[key].setStyleSheet(f"color: {color}; font-size: 12px;")


class CommandDisplay(QWidget):
    """Отображение команд и ответов."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 20, 40, 180); border: 1px solid rgb(0, 191, 255); border-radius: 5px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок
        title = QLabel("COMMAND LOG")
        title.setStyleSheet("color: rgb(0, 255, 255); font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        # Команды
        self.command_label = QLabel("Готов к работе...")
        self.command_label.setStyleSheet("color: rgb(255, 255, 255); font-size: 16px;")
        self.command_label.setWordWrap(True)
        layout.addWidget(self.command_label)

        # Ответ
        self.response_label = QLabel("")
        self.response_label.setStyleSheet("color: rgb(0, 191, 255); font-size: 14px;")
        self.response_label.setWordWrap(True)
        layout.addWidget(self.response_label)

        layout.addStretch()

    def show_command(self, command: str, response: str = ""):
        self.command_label.setText(f"> {command}")
        self.response_label.setText(response)


class JarvisHUD(QMainWindow):
    """Главное окно HUD JARVIS."""

    command_signal = pyqtSignal(str)

    def __init__(self, brain=None):
        super().__init__()
        self.brain = brain

        # Настройки окна
        self.setWindowTitle("JARVIS Ultimate HUD")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 10, 20, 255),
                    stop:1 rgba(0, 30, 60, 255));
            }
        """)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Левая панель - статус
        left_panel = QVBoxLayout()

        self.status_panel = StatusPanel()
        left_panel.addWidget(self.status_panel)

        self.command_display = CommandDisplay()
        left_panel.addWidget(self.command_display)

        left_panel.addStretch()
        main_layout.addLayout(left_panel)

        # Центр - дуговой реактор
        center_panel = QVBoxLayout()
        center_panel.addStretch()

        self.arc_reactor = ArcReactorWidget()
        center_panel.addWidget(self.arc_reactor, alignment=Qt.AlignCenter)

        # Название
        title = QLabel("J.A.R.V.I.S")
        title.setStyleSheet("color: rgb(0, 255, 255); font-size: 32px; font-weight: bold; letter-spacing: 5px;")
        title.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(title)

        subtitle = QLabel("Just A Rather Very Intelligent System")
        subtitle.setStyleSheet("color: rgb(0, 191, 255); font-size: 12px;")
        subtitle.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(subtitle)

        center_panel.addStretch()
        main_layout.addLayout(center_panel)

        # Правая панель - информация
        right_panel = QVBoxLayout()

        # Время
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: rgb(0, 255, 255); font-size: 48px; font-weight: bold;")
        self.time_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.time_label)

        # Дата
        self.date_label = QLabel()
        self.date_label.setStyleSheet("color: rgb(0, 191, 255); font-size: 16px;")
        self.date_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.date_label)

        right_panel.addSpacing(30)

        # Системная информация
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: rgba(0, 20, 40, 180); border: 1px solid rgb(0, 191, 255); border-radius: 5px;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(15, 15, 15, 15)

        info_title = QLabel("SYSTEM INFO")
        info_title.setStyleSheet("color: rgb(0, 255, 255); font-size: 14px; font-weight: bold;")
        info_layout.addWidget(info_title)

        self.info_labels = {}
        info_items = ["Hostname", "IP Address", "Uptime", "Processes"]

        for item in info_items:
            row = QHBoxLayout()
            label = QLabel(f"{item}:")
            label.setStyleSheet("color: rgb(0, 191, 255); font-size: 12px;")
            row.addWidget(label)

            value = QLabel("-")
            value.setStyleSheet("color: rgb(255, 255, 255); font-size: 12px;")
            row.addWidget(value)

            row.addStretch()
            info_layout.addLayout(row)
            self.info_labels[item] = value

        info_layout.addStretch()
        right_panel.addWidget(info_widget)

        right_panel.addStretch()
        main_layout.addLayout(right_panel)

        # Таймер обновления
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_info)
        self.update_timer.start(1000)

        # Начальное обновление
        self._update_info()

    def _update_info(self):
        """Обновление информации."""
        from datetime import datetime

        # Время
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%d %B %Y"))

        # Системная информация
        if self.brain:
            try:
                import socket
                import psutil

                hostname = socket.gethostname()
                self.info_labels["Hostname"].setText(hostname)

                # IP (упрощённо)
                self.info_labels["IP Address"].setText("192.168.1.100")

                # Uptime
                boot_time = psutil.boot_time()
                uptime = datetime.now() - datetime.fromtimestamp(boot_time)
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.info_labels["Uptime"].setText(f"{hours}h {minutes}m")

                # Processes
                proc_count = len(psutil.pids())
                self.info_labels["Processes"].setText(str(proc_count))

                # Статусы
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent

                self.status_panel.update_status("CPU", f"{cpu:.1f}%", 
                    "rgb(0, 255, 128)" if cpu < 70 else "rgb(255, 128, 0)")
                self.status_panel.update_status("RAM", f"{ram:.1f}%",
                    "rgb(0, 255, 128)" if ram < 80 else "rgb(255, 128, 0)")

            except Exception as e:
                pass

    def set_status(self, status: str):
        """Установить статус системы."""
        self.arc_reactor.set_status(status)

    def show_command(self, command: str, response: str = ""):
        """Показать команду и ответ."""
        self.command_display.show_command(command, response)

    def set_voice_active(self, active: bool):
        """Установить статус голосовой активности."""
        if active:
            self.status_panel.update_status("Voice", "LISTENING", "rgb(0, 255, 128)")
        else:
            self.status_panel.update_status("Voice", "IDLE", "rgb(0, 191, 255)")


def run_hud(brain=None):
    """Запуск HUD интерфейса."""
    app = QApplication(sys.argv)

    # Установка шрифта
    font = QFont("Arial", 10)
    app.setFont(font)

    hud = JarvisHUD(brain)
    hud.show()

    return app.exec_()


if __name__ == "__main__":
    run_hud()
