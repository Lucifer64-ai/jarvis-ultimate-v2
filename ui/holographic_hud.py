"""
Голографический HUD JARVIS (стиль Железного Человека)
- Полноэкранный overlay поверх рабочего стола
- Полупрозрачный, всегда поверх других окон
- Отображает метрики системы, время, состояние ассистента
"""

import threading
import time
from typing import Dict, Optional

try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class HolographicHUD:
    """Голографический HUD - полноэкранный интерфейс поверх рабочего стола."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Конфигурация
        config = brain.config.get("holographic_hud", {})
        self.enabled = config.get("enabled", True)
        self.fullscreen = config.get("fullscreen", True)
        self.opacity = config.get("opacity", 0.85)  # 0.0 - 1.0
        self.refresh_rate = config.get("refresh_rate", 1000)  # мс
        self.width = config.get("width", 1280)
        self.height = config.get("height", 720)
        self.position_x = config.get("position_x", 0)
        self.position_y = config.get("position_y", 0)

        # Цвета в стиле JARVIS (голографический синий)
        self.colors = {
            "bg": "#0a0a1a",
            "panel": "#1a1a3a",
            "accent": "#00ffff",
            "text": "#e0e0ff",
            "warning": "#ffaa00",
            "error": "#ff5555",
            "success": "#00ffaa",
        }

        # Состояние
        self.root: Optional[tk.Tk] = None
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        self.widgets: Dict[str, object] = {}

    def start(self) -> Dict:
        """Запуск HUD."""
        if not self.enabled:
            return {"status": "ok", "message": "HUD отключен в конфиге"}

        if not TKINTER_AVAILABLE:
            return {"status": "error", "message": "tkinter не доступен"}

        if self.running:
            return {"status": "ok", "message": "HUD уже запущен"}

        self.running = True
        self.update_thread = threading.Thread(target=self._run_hud, daemon=True)
        self.update_thread.start()

        self.logger.info("Голографический HUD запущен")
        return {"status": "ok", "message": "Голографический HUD запущен"}

    def stop(self) -> Dict:
        """Остановка HUD."""
        self.running = False
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass
            self.root = None
        self.logger.info("Голографический HUD остановлен")
        return {"status": "ok", "message": "Голографический HUD остановлен"}

    def _run_hud(self):
        """Запуск основного цикла HUD (в отдельном потоке)."""
        try:
            self.root = tk.Tk()
            self._setup_window()
            self._create_widgets()
            self._start_updates()
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Ошибка запуска HUD: {e}")
            self.running = False

    def _setup_window(self):
        """Настройка окна HUD."""
        root = self.root
        root.title("JARVIS HUD")

        # Полноэкранный режим
        if self.fullscreen:
            root.attributes('-fullscreen', True)
            root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        else:
            root.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")

        # Всегда поверх других окон
        root.attributes('-topmost', True)

        # Полупрозрачность
        try:
            root.attributes('-alpha', self.opacity)
        except Exception:
            pass

        # Цвет фона
        root.configure(bg=self.colors["bg"])

        # Убираем декорации окна
        root.overrideredirect(True)

        # Выход по клавише Escape
        root.bind('<Escape>', lambda e: self.stop())
        root.bind('<q>', lambda e: self.stop())

    def _create_widgets(self):
        """Создание виджетов HUD."""
        root = self.root

        # Заголовок
        title_label = tk.Label(
            root,
            text="J.A.R.V.I.S.",
            font=("Courier", 24, "bold"),
            fg=self.colors["accent"],
            bg=self.colors["bg"]
        )
        title_label.pack(anchor="nw", padx=30, pady=20)
        self.widgets["title"] = title_label

        # Подзаголовок с версией
        version_label = tk.Label(
            root,
            text="Just A Rather Very Intelligent System",
            font=("Courier", 12),
            fg=self.colors["text"],
            bg=self.colors["bg"]
        )
        version_label.pack(anchor="nw", padx=30)

        # Панель времени
        time_frame = tk.Frame(root, bg=self.colors["panel"], bd=2, relief="raised")
        time_frame.pack(anchor="nw", padx=30, pady=20, fill="x")

        time_label = tk.Label(
            time_frame,
            text="00:00:00",
            font=("Courier", 48, "bold"),
            fg=self.colors["accent"],
            bg=self.colors["panel"]
        )
        time_label.pack(padx=20, pady=10)
        self.widgets["time"] = time_label

        date_label = tk.Label(
            time_frame,
            text="",
            font=("Courier", 14),
            fg=self.colors["text"],
            bg=self.colors["panel"]
        )
        date_label.pack(padx=20, pady=(0, 10))
        self.widgets["date"] = date_label

        # Панель метрик системы
        metrics_frame = tk.Frame(root, bg=self.colors["panel"], bd=2, relief="raised")
        metrics_frame.pack(anchor="nw", padx=30, pady=20, fill="x")

        metrics_title = tk.Label(
            metrics_frame,
            text="СИСТЕМНЫЕ МЕТРИКИ",
            font=("Courier", 12, "bold"),
            fg=self.colors["warning"],
            bg=self.colors["panel"]
        )
        metrics_title.pack(anchor="w", padx=20, pady=(10, 5))

        cpu_label = tk.Label(
            metrics_frame,
            text="CPU: --%",
            font=("Courier", 14),
            fg=self.colors["text"],
            bg=self.colors["panel"]
        )
        cpu_label.pack(anchor="w", padx=20)
        self.widgets["cpu"] = cpu_label

        ram_label = tk.Label(
            metrics_frame,
            text="RAM: --%",
            font=("Courier", 14),
            fg=self.colors["text"],
            bg=self.colors["panel"]
        )
        ram_label.pack(anchor="w", padx=20)
        self.widgets["ram"] = ram_label

        disk_label = tk.Label(
            metrics_frame,
            text="Диск: --%",
            font=("Courier", 14),
            fg=self.colors["text"],
            bg=self.colors["panel"]
        )
        disk_label.pack(anchor="w", padx=20)
        self.widgets["disk"] = disk_label

        temp_label = tk.Label(
            metrics_frame,
            text="Темп: --°C",
            font=("Courier", 14),
            fg=self.colors["text"],
            bg=self.colors["panel"]
        )
        temp_label.pack(anchor="w", padx=20, pady=(0, 10))
        self.widgets["temp"] = temp_label

        # Панель состояния ассистента
        status_frame = tk.Frame(root, bg=self.colors["panel"], bd=2, relief="raised")
        status_frame.pack(anchor="nw", padx=30, pady=20, fill="x")

        status_title = tk.Label(
            status_frame,
            text="СОСТОЯНИЕ АССИСТЕНТА",
            font=("Courier", 12, "bold"),
            fg=self.colors["success"],
            bg=self.colors["panel"]
        )
        status_title.pack(anchor="w", padx=20, pady=(10, 5))

        status_label = tk.Label(
            status_frame,
            text="Онлайн",
            font=("Courier", 14, "bold"),
            fg=self.colors["success"],
            bg=self.colors["panel"]
        )
        status_label.pack(anchor="w", padx=20, pady=(0, 10))
        self.widgets["assistant_status"] = status_label

        # Подсказка управления
        hint_label = tk.Label(
            root,
            text="Нажмите ESC или Q для выхода",
            font=("Courier", 10),
            fg=self.colors["text"],
            bg=self.colors["bg"]
        )
        hint_label.pack(anchor="se", padx=20, pady=20)

    def _start_updates(self):
        """Запуск периодического обновления данных HUD."""
        self._update_loop()

    def _update_loop(self):
        """Цикл обновления данных на HUD."""
        if not self.running or not self.root:
            return

        try:
            # Время
            now = time.localtime()
            time_str = time.strftime("%H:%M:%S", now)
            date_str = time.strftime("%d %B %Y", now)

            if "time" in self.widgets:
                self.widgets["time"].config(text=time_str)
            if "date" in self.widgets:
                self.widgets["date"].config(text=date_str)

            # Метрики системы
            if hasattr(self.brain, 'system_monitor') and self.brain.system_monitor:
                metrics = self.brain.system_monitor.get_current_metrics()
                if metrics.get("status") == "ok":
                    cpu = metrics.get("cpu", 0)
                    ram = metrics.get("ram", 0)
                    disk = metrics.get("disk", 0)
                    temp = metrics.get("temperature", 0)

                    if "cpu" in self.widgets:
                        self.widgets["cpu"].config(text=f"CPU: {cpu:.0f}%")
                    if "ram" in self.widgets:
                        self.widgets["ram"].config(text=f"RAM: {ram:.0f}%")
                    if "disk" in self.widgets:
                        self.widgets["disk"].config(text=f"Диск: {disk:.0f}%")
                    if "temp" in self.widgets:
                        temp_text = f"Темп: {temp:.0f}°C" if temp > 0 else "Темп: N/A"
                        self.widgets["temp"].config(text=temp_text)

            # Статус ассистента
            if "assistant_status" in self.widgets:
                self.widgets["assistant_status"].config(text="Онлайн")

        except Exception as e:
            self.logger.error(f"Ошибка обновления HUD: {e}")

        # Планируем следующее обновление
        if self.running and self.root:
            self.root.after(self.refresh_rate, self._update_loop)

    def get_status(self) -> Dict:
        """Получить статус HUD."""
        return {
            "status": "ok",
            "enabled": self.enabled,
            "running": self.running,
            "fullscreen": self.fullscreen,
            "opacity": self.opacity,
            "tkinter_available": TKINTER_AVAILABLE
        }
