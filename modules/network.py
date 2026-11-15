"""
Сетевые операции JARVIS.
"""

from concurrent.futures import Future, ThreadPoolExecutor
import threading
import uuid
from typing import Dict

import requests

try:
    import speedtest
except ImportError:
    speedtest = None


class NetworkModule:
    """Сетевые функции с фоновым выполнением ресурсоёмких операций."""

    def __init__(self, brain):
        self.brain = brain
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="jarvis-network")
        self._lock = threading.Lock()
        self._speed_future: Future | None = None
        self._speed_job_id: str | None = None
        self._speed_result: Dict | None = None

    def get_ip(self) -> Dict:
        """Получить IP адрес."""
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            response.raise_for_status()
            return {"status": "ok", "ip": response.json()['ip']}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def speed_test(self) -> Dict:
        """Запустить фоновый тест скорости сети в фоновом потоке.

        Результат можно получить через get_speed_test_status(); последний запущенный
        тест в фоне возвращает результаты после завершения задания.
        """
        with self._lock:
            if self._speed_future and not self._speed_future.done():
                return {"status": "pending", "job_id": self._speed_job_id,
                        "message": "Тест сети уже выполняется"}

            self._speed_job_id = uuid.uuid4().hex
            self._speed_result = None
            self._speed_future = self._executor.submit(self._run_speed_test)
            self._speed_future.add_done_callback(self._on_speed_test_done)
            return {"status": "pending", "job_id": self._speed_job_id,
                    "message": "Тест сети запущен в фоне"}

    @staticmethod
    def _run_speed_test() -> Dict:
        """Выполнить блокирующие измерения в worker-потоке."""
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1_000_000
            upload = st.upload() / 1_000_000
            return {
                "status": "ok",
                "download": round(download, 2),
                "upload": round(upload, 2),
                "ping": round(st.results.ping, 2),
                "unit": "Mbps"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _on_speed_test_done(self, future: Future) -> None:
        try:
            result = future.result()
        except Exception as e:
            result = {"status": "error", "message": str(e)}
        with self._lock:
            self._speed_result = result
        self.brain.logger.info("Результат теста сети получен: %s", result)

    def get_speed_test_status(self, job_id: str | None = None) -> Dict:
        """Получить статус последнего запущенного теста сети."""
        with self._lock:
            if job_id and job_id != self._speed_job_id:
                return {"status": "error", "message": "Задача не найдена"}
            if self._speed_future is None:
                return {"status": "idle", "message": "Тест ещё не запускался"}
            if self._speed_result is not None:
                return {"job_id": self._speed_job_id, **self._speed_result}
            return {"status": "pending", "job_id": self._speed_job_id}

    def check_connection(self) -> Dict:
        """Проверить подключение к интернету."""
        try:
            response = requests.get('https://www.google.com', timeout=5)
            response.raise_for_status()
            return {"status": "ok", "connected": True}
        except requests.RequestException:
            return {"status": "ok", "connected": False}

    def close(self) -> None:
        """Закрыть пул потоков без ожидания завершения задач."""
        self._executor.shutdown(wait=False, cancel_futures=True)
