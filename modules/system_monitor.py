"""
Мониторинг системы JARVIS (стиль Железного Человека)
- Мониторинг CPU, RAM, диска, сети, температуры
- Отслеживание процессов
- Предупреждения при критических значениях
- История метрик для отображения на HUD
"""

import threading
import time
from collections import deque
from typing import Dict, List, Optional
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class SystemMonitor:
    """Мониторинг системы в реальном времени для JARVIS HUD."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Конфигурация
        config = brain.config.get("system_monitor", {})
        self.enabled = config.get("enabled", True)
        self.monitor_interval = config.get("interval", 5)  # секунды
        self.history_size = config.get("history_size", 60)  # количество точек истории

        # Состояние
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # История метрик (для отображения на HUD графиках)
        self.cpu_history: deque = deque(maxlen=self.history_size)
        self.ram_history: deque = deque(maxlen=self.history_size)
        self.network_history: deque = deque(maxlen=self.history_size)
        self.temp_history: deque = deque(maxlen=self.history_size)

        # Текущие значения
        self.current_cpu = 0.0
        self.current_ram = 0.0
        self.current_disk = 0.0
        self.current_temp = 0.0
        self.current_network_sent = 0
        self.current_network_recv = 0
        self.current_network_speed = 0.0

        # Информация о системе
        self.hostname = ""
        self.os_info = ""
        self.boot_time = 0

        # Последняя отправка сетевого трафика
        self._last_net_sent = 0
        self._last_net_recv = 0
        self._last_net_time = 0

    def start(self) -> Dict:
        """Запуск мониторинга."""
        if not self.enabled:
            return {"status": "ok", "message": "Мониторинг системы отключен"}

        if not PSUTIL_AVAILABLE:
            return {"status": "error", "message": "psutil не установлен"}

        if self.running:
            return {"status": "ok", "message": "Уже запущен"}

        self.running = True
        self._init_system_info()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Мониторинг системы запущен")
        return {"status": "ok", "message": "Мониторинг системы запущен"}

    def stop(self) -> Dict:
        """Остановка мониторинга."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("Мониторинг системы остановлен")
        return {"status": "ok", "message": "Мониторинг системы остановлен"}

    def _init_system_info(self):
        """Инициализация статической информации о системе."""
        try:
            import socket
            self.hostname = socket.gethostname()
            self.boot_time = psutil.boot_time()

            # Информация об ОС
            import platform
            self.os_info = f"{platform.system()} {platform.release()}"
        except Exception as e:
            self.logger.error(f"Ошибка инициализации информации о системе: {e}")

    def _monitor_loop(self):
        """Основной цикл мониторинга."""
        while self.running:
            try:
                self._collect_metrics()
                time.sleep(self.monitor_interval)
            except Exception as e:
                self.logger.error(f"Ошибка сбора метрик: {e}")
                time.sleep(self.monitor_interval)

    def _collect_metrics(self):
        """Сбор метрик системы."""
        if not PSUTIL_AVAILABLE:
            return

        now = time.time()

        # CPU
        cpu = psutil.cpu_percent(interval=None)
        self.current_cpu = cpu
        self.cpu_history.append({"timestamp": now, "value": cpu})

        # RAM
        ram = psutil.virtual_memory()
        self.current_ram = ram.percent
        self.ram_history.append({"timestamp": now, "value": ram.percent})

        # Диск
        disk = psutil.disk_usage('/')
        self.current_disk = disk.percent

        # Температура (если доступна)
        temp = self._get_cpu_temperature()
        if temp is not None:
            self.current_temp = temp
            self.temp_history.append({"timestamp": now, "value": temp})

        # Сеть
        net = psutil.net_io_counters()
        if self._last_net_time > 0:
            dt = now - self._last_net_time
            if dt > 0:
                speed = ((net.bytes_sent - self._last_net_sent) +
                         (net.bytes_recv - self._last_net_recv)) / dt / (1024 * 1024)
                self.current_network_speed = max(0, speed)
                self.network_history.append({"timestamp": now, "value": self.current_network_speed})

        self._last_net_sent = net.bytes_sent
        self._last_net_recv = net.bytes_recv
        self._last_net_time = now
        self.current_network_sent = net.bytes_sent
        self.current_network_recv = net.bytes_recv

    def _get_cpu_temperature(self) -> Optional[float]:
        """Получение температуры процессора."""
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return None
            # Ищем температуру CPU
            for name, entries in temps.items():
                if 'core' in name.lower() or 'cpu' in name.lower() or 'k10temp' in name.lower():
                    if entries:
                        return entries[0].current
            # Запасной вариант: первая доступная температура
            for entries in temps.values():
                if entries:
                    return entries[0].current
        except Exception:
            pass
        return None

    def get_current_metrics(self) -> Dict:
        """Получить текущие метрики."""
        return {
            "status": "ok",
            "cpu": self.current_cpu,
            "ram": self.current_ram,
            "disk": self.current_disk,
            "temperature": self.current_temp,
            "network_speed": self.current_network_speed,
            "network_sent": self.current_network_sent,
            "network_recv": self.current_network_recv,
            "timestamp": time.time()
        }

    def get_history(self, metric: str = "cpu") -> Dict:
        """Получить историю метрик."""
        history_map = {
            "cpu": self.cpu_history,
            "ram": self.ram_history,
            "network": self.network_history,
            "temperature": self.temp_history,
        }
        hist = history_map.get(metric, self.cpu_history)
        return {
            "status": "ok",
            "metric": metric,
            "data": list(hist),
            "count": len(hist)
        }

    def get_processes(self, limit: int = 10) -> Dict:
        """Получить список процессов (по загрузке CPU)."""
        if not PSUTIL_AVAILABLE:
            return {"status": "error", "message": "psutil не установлен"}

        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append({
                        "pid": info['pid'],
                        "name": info['name'] or "unknown",
                        "cpu": info['cpu_percent'] or 0,
                        "memory": info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            processes.sort(key=lambda x: x['cpu'], reverse=True)
            return {
                "status": "ok",
                "processes": processes[:limit],
                "count": len(processes)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_system_info(self) -> Dict:
        """Получить статическую информацию о системе."""
        import time
        uptime = int(time.time() - self.boot_time) if self.boot_time else 0
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60

        return {
            "status": "ok",
            "hostname": self.hostname,
            "os": self.os_info,
            "uptime_hours": hours,
            "uptime_minutes": minutes,
            "uptime_formatted": f"{hours}ч {minutes}м",
        }

    def get_disk_info(self) -> Dict:
        """Получить информацию о дисках."""
        if not PSUTIL_AVAILABLE:
            return {"status": "error", "message": "psutil не установлен"}

        try:
            disks = []
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disks.append({
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    })
                except Exception:
                    continue
            return {"status": "ok", "disks": disks}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_battery_info(self) -> Dict:
        """Получить информацию о батарее."""
        if not PSUTIL_AVAILABLE:
            return {"status": "error", "message": "psutil не установлен"}

        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return {"status": "ok", "message": "Батарея не обнаружена (настольный ПК)"}

            return {
                "status": "ok",
                "percent": battery.percent,
                "plugged": battery.power_plugged,
                "seconds_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNKNOWN else None,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict:
        """Получить статус мониторинга."""
        return {
            "status": "ok",
            "enabled": self.enabled,
            "running": self.running,
            "interval": self.monitor_interval,
            "psutil_available": PSUTIL_AVAILABLE,
            "current_cpu": self.current_cpu,
            "current_ram": self.current_ram,
            "current_disk": self.current_disk,
            "current_temp": self.current_temp,
        }
