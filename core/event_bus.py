"""
¡иµ¼° ¾±и¹ JARVIS
"""

from typing import Dict, List, Callable
from collections import defaultdict
import threading


class EventBus:
    """¨и½° ¾±и¹ ´» в·и ¼µ¶´ ¼¾´»¼и."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._events: List[Dict] = []
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, callback: Callable):
        self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        if callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)

    def emit(self, event_type: str, data: Dict = None):
        event = {"type": event_type, "data": data or {}}
        with self._lock:
            self._events.append(event)


    def publish(self, event_type: str, data: Dict = None):
        """»¸° для emit() - ¿±»¸º°¸ ¾±¸."""
        self.emit(event_type, data)

    def process_events(self):
        with self._lock:
            events = self._events.copy()
            self._events.clear()

        for event in events:
            for listener in self._listeners.get(event["type"], []):
                try:
                    listener(event["data"])
                except Exception as e:
                    print(f"и±º° ¾±°±¾иº° ¾±и: {e}")

    def clear(self):
        self._listeners.clear()
        self._events.clear()
