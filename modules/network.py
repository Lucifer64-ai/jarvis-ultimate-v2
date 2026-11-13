"""
¡µµ²µ ¾¿µ°¸¸ JARVIS.
"""

from concurrent.futures import Future, ThreadPoolExecutor
import threading
import uuid
from typing import Dict

import requests
import speedtest


class NetworkModule:
    """¡µµ²µ ½º¸¸  ¾½¾²¼ ²¿¾»½µ½¸µ¼ µ° º¾¾¸."""

    def __init__(self, brain):
        self.brain = brain
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="jarvis-network")
        self._lock = threading.Lock()
        self._speed_future: Future | None = None
        self._speed_job_id: str | None = None
        self._speed_result: Dict | None = None

    def get_ip(self) -> Dict:
        """¾»¸ IP °´µ."""
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            response.raise_for_status()
            return {"status": "ok", "ip": response.json()['ip']}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def speed_test(self) -> Dict:
        """¾°²¸ ´»¸µ»½¹ µ º¾¾¸ ² ¾½¾² ¾µµ´.

         µ·»° ¼¾¶½¾ ¿¾»¸ µµ· get_speed_test_status(); ¿¾²¾½¹ ²·¾²
        ²¾ ²µ¼ ²¿¾»½µ½¸ ²¾·²°°µ ¸´µ½¸¸º°¾ ¶µ ·°¿µ½½¾¹ ·°´°¸.
        """
        with self._lock:
            if self._speed_future and not self._speed_future.done():
                return {"status": "pending", "job_id": self._speed_job_id,
                        "message": "¢µ º¾¾¸ ¶µ ²¿¾»½µ"}

            self._speed_job_id = uuid.uuid4().hex
            self._speed_result = None
            self._speed_future = self._executor.submit(self._run_speed_test)
            self._speed_future.add_done_callback(self._on_speed_test_done)
            return {"status": "pending", "job_id": self._speed_job_id,
                    "message": "¢µ º¾¾¸ ·°¿µ½ ² ¾½µ"}

    @staticmethod
    def _run_speed_test() -> Dict:
        """¿¾»½¸ ±»¾º¸ °±¾ ² worker-¿¾¾ºµ."""
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
        self.brain.logger.info("¾²µº° º¾¾¸ ·°²µµ½°: %s", result)

    def get_speed_test_status(self, job_id: str | None = None) -> Dict:
        """¾»¸ ° ¿¾»µ´½µ¹ ¿¾²µº¸ º¾¾¸."""
        with self._lock:
            if job_id and job_id != self._speed_job_id:
                return {"status": "error", "message": "°´°° ½µ ½°¹´µ½°"}
            if self._speed_future is None:
                return {"status": "idle", "message": "¾²µº° µ ½µ ·°¿º°»°"}
            if self._speed_result is not None:
                return {"job_id": self._speed_job_id, **self._speed_result}
            return {"status": "pending", "job_id": self._speed_job_id}

    def check_connection(self) -> Dict:
        """¾²µ¸ ¿¾´º»µ½¸µ º ¸½µ½µ."""
        try:
            response = requests.get('https://www.google.com', timeout=5)
            response.raise_for_status()
            return {"status": "ok", "connected": True}
        except requests.RequestException:
            return {"status": "ok", "connected": False}

    def close(self) -> None:
        """°½¾²¸ ¾µµ´ ¾½¾² ·°´° ±µ· ¾¶¸´°½¸ ·°²µµ½¸ µ°."""
        self._executor.shutdown(wait=False, cancel_futures=True)
