"""
Управление процессами Windows для JARVIS
"""

import subprocess
import psutil
from typing import Dict, List, Optional


class ProcessManager:
    """Управление процессами Windows."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

    def list_processes(self, limit: int = 20) -> Dict:
        """Получить список запущенных процессов."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'cpu': info['cpu_percent'],
                        'memory_mb': round(info['memory_info'].rss / 1024 / 1024, 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Сортировка по использованию CPU
            processes.sort(key=lambda x: x['cpu'], reverse=True)

            return {
                "status": "ok",
                "count": len(processes),
                "processes": processes[:limit]
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения списка процессов: {e}")
            return {"status": "error", "message": str(e)}

    def find_process(self, name: str) -> Dict:
        """Найти процесс по имени."""
        try:
            found = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        info = proc.info
                        found.append({
                            'pid': info['pid'],
                            'name': info['name'],
                            'cpu': info['cpu_percent'],
                            'memory_mb': round(info['memory_info'].rss / 1024 / 1024, 2)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return {
                "status": "ok",
                "found": len(found),
                "processes": found
            }
        except Exception as e:
            self.logger.error(f"Ошибка поиска процесса: {e}")
            return {"status": "error", "message": str(e)}

    def kill_process(self, pid: int) -> Dict:
        """Завершить процесс по PID."""
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            proc.terminate()
            proc.wait(timeout=5)
            self.logger.info(f"Процесс {name} (PID {pid}) завершен")
            return {"status": "ok", "message": f"Процесс {name} завершен"}
        except psutil.NoSuchProcess:
            return {"status": "error", "message": f"Процесс с PID {pid} не найден"}
        except psutil.TimeoutExpired:
            return {"status": "error", "message": f"Процесс {pid} не отвечает, требуется принудительное завершение"}
        except Exception as e:
            self.logger.error(f"Ошибка завершения процесса: {e}")
            return {"status": "error", "message": str(e)}

    def kill_process_by_name(self, name: str) -> Dict:
        """Завершить процесс по имени."""
        try:
            killed = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        proc.wait(timeout=5)
                        killed.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass

            if killed:
                self.logger.info(f"Завершены процессы: {', '.join(killed)}")
                return {"status": "ok", "message": f"Завершено процессов: {len(killed)}", "names": killed}
            else:
                return {"status": "error", "message": f"Процесс {name} не найден"}
        except Exception as e:
            self.logger.error(f"Ошибка завершения процесса по имени: {e}")
            return {"status": "error", "message": str(e)}

    def get_system_info(self) -> Dict:
        """Получить информацию о системе."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "status": "ok",
                "cpu": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count(logical=False),
                    "threads": psutil.cpu_count(logical=True)
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": disk.percent
                }
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения системной информации: {e}")
            return {"status": "error", "message": str(e)}

    def get_top_processes(self, by: str = "cpu", limit: int = 10) -> Dict:
        """Получить топ процессов по CPU или памяти."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'cpu': info['cpu_percent'],
                        'memory_mb': round(info['memory_info'].rss / 1024 / 1024, 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if by == "memory":
                processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            else:
                processes.sort(key=lambda x: x['cpu'], reverse=True)

            return {
                "status": "ok",
                "sorted_by": by,
                "processes": processes[:limit]
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения топ процессов: {e}")
            return {"status": "error", "message": str(e)}
