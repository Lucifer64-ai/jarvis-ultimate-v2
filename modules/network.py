"""
¡µµвµ ¾¿µ°ии JARVIS.
"""

from concurrent.futures import Future, ThreadPoolExecutor
import threading
import uuid
from typing import Dict

import requests
import speedtest


class NetworkModule:
    """¡µµвµ ½ºии  ¾½¾в¼ в¿¾»ни½иµ¼ µ° º¾¾и."""

    def __init__(self, brain):
        self.brain = brain
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="jarvis-network")
        self._lock = threading.Lock()
        self._speed_future: Future | None = None
        self._speed_job_id: str | None = None
        self._speed_result: Dict | None = None

    def get_ip(self) -> Dict:
        """¾»и IP °´µ."""
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            response.raise_for_status()
            return {"status": "ok", "ip": response.json()['ip']}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def speed_test(self) -> Dict:
        """¾°ви ´»иµ»½¹ µ º¾¾и в ¾½¾в ¾µµ´.

         µ·»° ¼¾¶½¾ ¿¾»и µµ· get_speed_test_status(); ¿¾в¾½¹ в·¾в
        в¾ вµ¼ в¿¾»ни½и в¾·в°°µ и´µ½ииº°¾ ¶µ ·°¿µ½½¾¹ ·°´°и.
        """
        with self._lock:
            if self._speed_future and not self._speed_future.done():
                return {"status": "pending", "job_id": self._speed_job_id,
                        "message": "¢µ º¾¾и ¶µ в¿¾»½µ"}

            self._speed_job_id = uuid.uuid4().hex
            self._speed_result = None
            self._speed_future = self._executor.submit(self._run_speed_test)
            self._speed_future.add_done_callback(self._on_speed_test_done)
            return {"status": "pending", "job_id": self._speed_job_id,
                    "message": "¢µ º¾¾и ·°¿µ½ в ¾ни"}

    @staticmethod
    def _run_speed_test() -> Dict:
        """¿¾»½и ±»¾ºи °±¾ в worker-¿¾¾ºµ."""
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
        self.brain.logger.info("¾вµº° º¾¾и ·°вµµ½°: %s", result)

    def get_speed_test_status(self, job_id: str | None = None) -> Dict:
        """¾»и ° ¿¾»µ´ни¹ ¿¾вµºи º¾¾и."""
        with self._lock:
            if job_id and job_id != self._speed_job_id:
                return {"status": "error", "message": "°´°° ни ½°¹´µ½°"}
            if self._speed_future is None:
                return {"status": "idle", "message": "¾вµº° µ ни ·°¿º°»°"}
            if self._speed_result is not None:
                return {"job_id": self._speed_job_id, **self._speed_result}
            return {"status": "pending", "job_id": self._speed_job_id}

    def check_connection(self) -> Dict:
        """¾вµи ¿¾´º»µ½иµ º и½µни."""
        try:
            response = requests.get('https://www.google.com', timeout=5)
            response.raise_for_status()
            return {"status": "ok", "connected": True}
        except requests.RequestException:
            return {"status": "ok", "connected": False}

    def close(self) -> None:
        """°½¾ви ¾µµ´ ¾½¾в ·°´° ±µ· ¾¶и´°½и ·°вµµ½и µ°."""
        self._executor.shutdown(wait=False, cancel_futures=True)
