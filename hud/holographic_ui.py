"""
Holographic HUD Interface - ¸°»½¾µ µ»¾ JARVIS
¾»¾³°¸µº¸¹ ¸½µµ¹ ¿¾²µ °±¾µ³¾ ¾»° ² ¸»µ Iron Man
"""

import math
import sys
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Optional

import psutil
from PyQt5.QtCore import Qt, QTimer, QRect, QRectF, QPointF, QPainterPath, pyqtSignal
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QRadialGradient
from PyQt5.QtWidgets import QApplication, QWidget, QPainter, QDesktopWidget


class HolographicHUD(QWidget):
    """¾»¾³°¸µº¸¹ HUD ¸½µµ¹ JARVIS."""

    status_requested = pyqtSignal(str)
    voice_requested = pyqtSignal(bool)
    optimization_requested = pyqtSignal(object)

    def __init__(self, brain=None):
        super().__init__()
        self.brain = brain
        self.setWindowTitle("JARVIS HUD")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(QDesktopWidget().screenGeometry())

        self.color_primary = QColor(0, 200, 255, 200)
        self.color_secondary = QColor(0, 150, 255, 150)
        self.color_accent = QColor(255, 150, 0, 200)
        self.color_text = QColor(200, 230, 255, 255)
        self.panel_brush = QBrush(QColor(0, 20, 40, 100))
        self.font_cpu = QFont("Arial", 24, QFont.Bold)
        self.font_title = QFont("Arial", 12, QFont.Bold)
        self.font_panel = QFont("Arial", 14)
        self.font_status = QFont("Arial", 16, QFont.Bold)

        self.animation_time = 0.0
        self.pulse_phase = 0
        self.cpu_usage = 0.0
        self.ram_usage = 0.0
        self.network_speed = 0.0
        self.status = "READY"
        self.voice_active = False
        self.optimization_recommendations = []

        self._metrics_future: Optional[Future] = None
        self._last_net = None
        self._last_net_time = None
        self._wave_x = [i * 4 for i in range(100)]

        self.status_requested.connect(self._apply_status)
        self.voice_requested.connect(self._apply_voice_active)
        self.optimization_requested.connect(self._apply_optimization_status)

        self._metrics_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="jarvis-hud-metrics")
        self._metrics_timer = QTimer(self)
        self._metrics_timer.timeout.connect(self.update_data)
        self._metrics_timer.start(1000)

        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self.animate)
        self._animation_timer.start(100)

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)

        self._metrics_future = self._metrics_executor.submit(self._read_metrics)
        self.show()

    def _read_metrics(self):
        """Read system counters on a worker; never block Qt's GUI event loop."""
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        counters = psutil.net_io_counters()
        return cpu, ram, counters.bytes_sent + counters.bytes_recv, time.monotonic()

    def update_data(self):
        future = self._metrics_future
        if future is not None and future.done():
            try:
                cpu, ram, total_bytes, now = future.result()
                changed = cpu != self.cpu_usage or ram != self.ram_usage
                self.cpu_usage, self.ram_usage = cpu, ram
                if self._last_net is not None and self._last_net_time is not None and now > self._last_net_time:
                    speed = max(0, total_bytes - self._last_net) / (now - self._last_net_time) / (1024 * 1024)
                    changed = changed or abs(speed - self.network_speed) >= 0.1
                    self.network_speed = speed
                self._last_net, self._last_net_time = total_bytes, now
                if changed:
                    self.update(QRect(0, 0, self.width(), self.height()))
            except Exception as exc:
                if self.brain:
                    self.brain.logger.debug("µ ´°»¾ ¾±½¾²¸ HUD ¼µ¸º¸: %s", exc)
            self._metrics_future = None

        if self._metrics_future is None:
            self._metrics_future = self._metrics_executor.submit(self._read_metrics)

    def _update_clock(self):
        self.update(QRect(35, 35, 330, 125))

    def animate(self):
        self.animation_time += 0.1
        self.pulse_phase = (self.pulse_phase + 1) % 360
        cx, cy = self.width() // 2, self.height() // 2
        self.update(QRect(cx - 240, cy - 240, 480, 480))
        if self.voice_active:
            self.update(QRect(cx - 210, cy + 150, 420, 100))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setClipRegion(event.region())
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.width(), self.height()
        center_x, center_y = width // 2, height // 2
        self.draw_arc_reactor(painter, center_x, center_y, 150)
        self.draw_system_panels(painter, width, height)
        if self.voice_active:
            self.draw_voice_wave(painter, center_x, center_y + 200)
        self.draw_status(painter, center_x, height - 100)
        painter.end()

    def draw_arc_reactor(self, painter: QPainter, x: int, y: int, radius: int):
        pulse = math.sin(self.animation_time * 2) * 0.2 + 0.8
        gradient = QRadialGradient(x, y, radius * 1.5)
        gradient.setColorAt(0, QColor(0, 200, 255, int(100 * pulse)))
        gradient.setColorAt(0.5, QColor(0, 150, 255, int(50 * pulse)))
        gradient.setColorAt(1, QColor(0, 100, 255, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(x, y), radius * 1.5, radius * 1.5)

        pen = QPen(self.color_primary, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(x, y), radius, radius)

        pen.setColor(self.color_secondary)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(x, y), radius * 0.7, radius * 0.7)

        painter.setBrush(QBrush(self.color_accent))
        painter.setPen(Qt.NoPen)
        for i in range(8):
            angle = math.radians((self.animation_time * 50 + i * 45) % 360)
            painter.drawEllipse(
                QPointF(
                    x + math.cos(angle) * radius * 0.85,
                    y + math.sin(angle) * radius * 0.85,
                ),
                5,
                5,
            )

        painter.setPen(QPen(self.color_text))
        painter.setFont(self.font_cpu)
        painter.drawText(QRectF(x - 50, y - 30, 100, 60), Qt.AlignCenter, f"{int(self.cpu_usage)}%")

    def draw_system_panels(self, painter: QPainter, width: int, height: int):
        self.draw_panel(painter, 50, 50, 300, 150, "TIME", [time.strftime("%H:%M:%S"), time.strftime("%d.%m.%Y")])
        self.draw_panel(painter, width - 350, 50, 300, 150, "MEMORY", [f"RAM: {self.ram_usage:.0f}%", f"CPU: {self.cpu_usage:.0f}%"])
        self.draw_panel(painter, 50, height - 200, 300, 150, "NETWORK", [f"Speed: {self.network_speed:.1f} MB/s", "Status: ONLINE"])
        items = ["¿¸¼¸·°¸"] + self.optimization_recommendations[:3]
        self.draw_panel(painter, width - 430, height - 250, 380, 200, "JARVIS / OPTIMIZATION", items)

    def draw_panel(self, painter: QPainter, x: int, y: int, w: int, h: int, title: str, data: list):
        painter.setPen(QPen(self.color_primary, 2))
        painter.setBrush(self.panel_brush)
        painter.drawRoundedRect(x, y, w, h, 10, 10)
        painter.setPen(QPen(self.color_accent))
        painter.setFont(self.font_title)
        painter.drawText(x + 10, y + 25, title)
        painter.setPen(QPen(self.color_text))
        painter.setFont(self.font_panel)
        for i, text in enumerate(data):
            painter.drawText(QRect(x + 10, y + 38 + i * 32, w - 20, 42), Qt.AlignLeft | Qt.TextWordWrap, text)

    def draw_voice_wave(self, painter: QPainter, x: int, y: int):
        painter.setPen(QPen(self.color_primary, 3))
        path = QPainterPath()
        for i, offset_x in enumerate(self._wave_x):
            point = QPointF(x - 200 + offset_x, y + math.sin(self.animation_time * 5 + i * 0.2) * 30)
            if i == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)
        painter.drawPath(path)

    def draw_status(self, painter: QPainter, x: int, y: int):
        painter.setPen(QPen(self.color_text))
        painter.setFont(self.font_status)
        painter.drawText(QRectF(x - 100, y, 200, 40), Qt.AlignCenter, self.status)

    def set_status(self, status: str):
        self.status_requested.emit(status)

    def _apply_status(self, status: str):
        if self.status != status:
            self.status = status
            self.update(QRect(self.width() // 2 - 120, self.height() - 110, 240, 60))

    def set_voice_active(self, active: bool):
        self.voice_requested.emit(active)

    def _apply_voice_active(self, active: bool):
        if self.voice_active != active:
            self.voice_active = active
            cx, cy = self.width() // 2, self.height() // 2
            self.update(QRect(cx - 220, cy + 140, 440, 120))

    def set_optimization_status(self, report: dict):
        """Queue optimization recommendations for safe GUI-thread rendering."""
        self.optimization_requested.emit(report or {})

    def _apply_optimization_status(self, report: dict):
        recommendations = report.get("recommendations", []) if isinstance(report, dict) else []
        self.optimization_recommendations = [str(item) for item in recommendations[:3]]
        self.update(QRect(self.width() - 450, self.height() - 270, 420, 230))

    def closeEvent(self, event):
        self._metrics_timer.stop()
        self._animation_timer.stop()
        self._clock_timer.stop()
        self._metrics_executor.shutdown(wait=False, cancel_futures=True)
        super().closeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = HolographicHUD()
    sys.exit(app.exec_())
