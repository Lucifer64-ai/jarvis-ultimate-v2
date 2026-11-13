"""
голосовые ¿¾µ°¼¸ JARVIS
"""

import psutil
from typing import Dict, List


class ProcessModule:
    """голосовые ¿¾µ°¼¸ ¸µ¼."""

    def __init__(self, brain):
        self.brain = brain

    def list_processes(self, limit: int = 20) -> List[Dict]:
        """¡¿¸¾º ·°¿µ½½ ¿¾µ¾²."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu": round(proc.info['cpu_percent'], 1),
                    "memory": round(proc.info['memory_percent'], 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        processes.sort(key=lambda x: x['cpu'], reverse=True)
        return processes[:limit]

    def kill_process(self, name: str) -> Dict:
        """°²µ¸ ¿¾µ ¿¾ ¸¼µ½¸."""
        killed = []
        for proc in psutil.process_iter(['name']):
            try:
                if name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    killed.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if killed:
            return {"status": "ok", "killed": killed}
        return {"status": "error", "message": f"¾µ '{name}' ни на¹´µ½"}

    def get_process_info(self, name: str) -> Dict:
        """½¾¼°¸ ¾ ¿¾µµ."""
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                if name.lower() in proc.info['name'].lower():
                    return {
                        "status": "ok",
                        "process": {
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu": round(proc.info['cpu_percent'], 1),
                            "memory": round(proc.info['memory_percent'], 1),
                            "status": proc.info['status']
                        }
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {"status": "error", "message": f"¾µ '{name}' ни на¹´µ½"}
