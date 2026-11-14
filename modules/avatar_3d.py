"""
3D Avatar Module - Голографический аватар JARVIS
Реагирует на голос и команды пользователя
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
    """Голографический 3D аватар JARVIS."""

    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.logger = brain.logger

        # Состояния работы
        self.state = "idle"  # idle, listening, speaking, thinking, processing
        self.voice_level = 0.0
        self.rotation_angle = 0.0
        self.pulse_phase = 0.0
        self.energy_level = 0.5

        # Настройки отображения
        self.width = 400
        self.height = 400
        self.position_x = 100
        self.position_y = 100

        # Анимации
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)  # ~60 FPS

        # Настройка окна
        self.setup_window()

        self.logger.info("⚡ 3D аватар инициализирован")

    def setup_window(self):
        """Настройка прозрачного окна."""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.setGeometry(self.position_x, self.position_y, self.width, self.height)

        # Прозрачность
        self.setWindowOpacity(0.85)

    def paintEvent(self, event):
        """Отрисовка голографического аватара."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Центр аватара
        center_x = self.width // 2
        center_y = self.height // 2

        # === ВНЕШНИЕ КОЛЬЦА (Arc Reactor стиль) ===

        # Внешнее кольцо
        outer_radius = 150
        self.draw_ring(painter, center_x, center_y, outer_radius, 20, 
                      QColor(0, 200, 255, 100), self.rotation_angle)

        # Белое кольцо
        middle_radius = 120
        self.draw_ring(painter, center_x, center_y, middle_radius, 15,
                      QColor(0, 255, 255, 150), -self.rotation_angle * 1.5)

        # Внутреннее кольцо
        inner_radius = 90
        self.draw_ring(painter, center_x, center_y, inner_radius, 10,
                      QColor(100, 255, 255, 200), self.rotation_angle * 2)

        # === ЯДРО (пульсирующий центр) ===

        # Размер пульсации
        pulse_size = 60 + math.sin(self.pulse_phase) * 10

        # Радиальный градиент
        gradient = QRadialGradient(center_x, center_y, pulse_size)
        gradient.setColorAt(0, QColor(255, 255, 255, 255))
        gradient.setColorAt(0.3, QColor(100, 255, 255, 200))
        gradient.setColorAt(0.7, QColor(0, 200, 255, 150))
        gradient.setColorAt(1, QColor(0, 100, 200, 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - pulse_size, center_y - pulse_size,
                           pulse_size * 2, pulse_size * 2)

        # === ЭНЕРГЕТИЧЕСКИЕ ЛИНИИ ===

        self.draw_energy_lines(painter, center_x, center_y, inner_radius, outer_radius)

        # === ИНДИКАТОР ГОЛОСА ===

        if self.voice_level > 0.1:
            self.draw_voice_indicator(painter, center_x, center_y, outer_radius + 30)

        # === ТЕКСТ СОСТОЯНИЯ ===

        self.draw_state_text(painter, center_x, self.height - 50)

        painter.end()

    def draw_ring(self, painter: QPainter, cx: int, cy: int, radius: int, 
                  thickness: int, color: QColor, rotation: float):
        """Отрисовка вращающегося кольца."""
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(rotation)

        # Сегменты кольца
        segments = 12
        for i in range(segments):
            angle = i * (360 / segments)
            painter.save()
            painter.rotate(angle)

            # Радиальный градиент сегмента
            gradient = QLinearGradient(0, -radius, 0, -radius + thickness)
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)

            # Рисуем сегмент
            painter.drawRoundedRect(-thickness // 2, -radius, thickness, thickness, 3, 3)

            painter.restore()

        painter.restore()

    def draw_energy_lines(self, painter: QPainter, cx: int, cy: int, 
                          inner_r: int, outer_r: int):
        """Отрисовка энергетических линий."""
        lines = 8
        for i in range(lines):
            angle = i * (360 / lines) + self.rotation_angle * 3
            rad = math.radians(angle)

            x1 = cx + math.cos(rad) * inner_r
            y1 = cy + math.sin(rad) * inner_r
            x2 = cx + math.cos(rad) * outer_r
            y2 = cy + math.sin(rad) * outer_r

            # Радиальный градиент линии
            gradient = QLinearGradient(x1, y1, x2, y2)
            gradient.setColorAt(0, QColor(0, 255, 255, 200))
            gradient.setColorAt(1, QColor(0, 255, 255, 0))

            pen = QPen(QBrush(gradient), 2)
            painter.setPen(pen)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def draw_voice_indicator(self, painter: QPainter, cx: int, cy: int, radius: int):
        """Отрисовка индикатора голоса."""
        # Волны голоса
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
        """Отрисовка текста состояния."""
        state_texts = {
            "idle": "ОЖИДАНИЕ",
            "listening": "СЛУШАЮ...",
            "speaking": "ГОВОРЮ...",
            "thinking": "ДУМАЮ...",
            "processing": "ОБРАБОТКА..."
        }

        text = state_texts.get(self.state, "ОЖИДАНИЕ")

        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)

        # Тень текста
        painter.setPen(QColor(0, 0, 0, 150))
        painter.drawText(x + 1, y + 1, text)

        # Основной текст
        painter.setPen(QColor(0, 255, 255, 255))
        painter.drawText(x, y, text)

    def update_animation(self):
        """Обновление анимации."""
        # Вращение
        self.rotation_angle += 1.0
        if self.rotation_angle >= 360:
            self.rotation_angle = 0

        # Пульсация
        self.pulse_phase += 0.1
        if self.pulse_phase >= 2 * math.pi:
            self.pulse_phase = 0

        # Затухание голоса
        if self.voice_level > 0:
            self.voice_level -= 0.05
            if self.voice_level < 0:
                self.voice_level = 0

        # Перерисовка
        self.update()

    # === УПРАВЛЕНИЕ АВАТАРОМ ===

    def set_state(self, state: str):
        """Установка состояния аватара."""
        if state in ["idle", "listening", "speaking", "thinking", "processing"]:
            self.state = state
            self.logger.debug(f"Аватар: состояние -> {state}")

    def set_voice_level(self, level: float):
        """Установка уровня голоса (0.0 - 1.0)."""
        self.voice_level = max(0.0, min(1.0, level))

    def set_energy_level(self, level: float):
        """Установка уровня энергии (0.0 - 1.0)."""
        self.energy_level = max(0.0, min(1.0, level))

    def show_avatar(self):
        """Показать аватар."""
        self.show()
        self.logger.info("Аватар показан")

    def hide_avatar(self):
        """Скрыть аватар."""
        self.hide()
        self.logger.info("Аватар скрыт")

    def move_to_position(self, x: int, y: int):
        """Перемещение аватара."""
        self.position_x = x
        self.position_y = y
        self.move(x, y)

    def resize_avatar(self, width: int, height: int):
        """Изменение размера аватара."""
        self.width = width
        self.height = height
        self.setFixedSize(width, height)


class AvatarManager:
    """Менеджер управления 3D аватаром."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.avatar: Optional[HolographicAvatar] = None
        self.app: Optional[QApplication] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False

    def initialize(self):
        """Инициализация аватара в отдельном потоке."""
        if self.running:
            self.logger.warning("Аватар уже запущен")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_avatar_thread, daemon=True)
        self.thread.start()

        # Ожидание инициализации
        time.sleep(0.5)

        self.logger.info("⚡ Менеджер аватара запущен")

    def _run_avatar_thread(self):
        """Поток для запуска Qt приложения."""
        try:
            self.app = QApplication(sys.argv)
            self.avatar = HolographicAvatar(self.brain)
            self.app.exec_()
        except Exception as e:
            self.logger.error(f"Ошибка потока аватара: {e}")
            self.running = False

    def set_state(self, state: str):
        """Установка состояния аватара."""
        if self.avatar:
            self.avatar.set_state(state)

    def set_voice_level(self, level: float):
        """Установка уровня голоса."""
        if self.avatar:
            self.avatar.set_voice_level(level)

    def show(self):
        """Показать аватар."""
        if self.avatar:
            self.avatar.show_avatar()

    def hide(self):
        """Скрыть аватар."""
        if self.avatar:
            self.avatar.hide_avatar()

    def shutdown(self):
        """Остановка аватара."""
        self.running = False
        if self.app:
            self.app.quit()
        self.logger.info("Аватар остановлен")
