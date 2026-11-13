"""Advanced optimization agents for JARVIS.

These agents do not mutate the system by themselves. They observe
resource pressure, cache repeated work, and prioritize likely repeated
workflow tasks by reusing the existing pattern-recognition data.
"""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List

try:
    import psutil
except ImportError:  # pragma: no cover - optional dependency
    psutil = None


class ResourceOptimizationAgent:
    """Monitor CPU and memory pressure and return safe recommendations."""

    def __init__(self, brain):
        self.brain = brain

    def analyze(self) -> Dict:
        config = self.brain.config
        cpu_threshold = config.get("optimization.cpu_threshold_percent", 80)
        memory_threshold = config.get("optimization.memory_threshold_percent", 85)
        recommendations: List[str] = []
        metrics = {"cpu_percent": None, "memory_percent": None, "active_processes": None}

        if psutil is None:
            return {
                "status": "unavailable",
                "metrics": metrics,
                "recommendations": [],
                "message": "¾½¸¾¸½³ µ¾² ½µ´¾¿µ½: psutil ½µ °½¾²»µ½",
            }

        try:
            metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
            metrics["memory_percent"] = psutil.virtual_memory().percent
            metrics["active_processes"] = len(psutil.pids())
        except Exception as error:
            self.brain.logger.debug("µ ´°»¾ ¿¾»¸ ¼µ¸º¸ µ¾²: %s", error)
            return {
                "status": "error",
                "metrics": metrics,
                "recommendations": [],
                "message": "µ ´°»¾ ¿¾»¸ ¼µ¸º¸ µ¾²",
            }

        if metrics["cpu_percent"] >= cpu_threshold:
            recommendations.append(
                "¾º° ½°³·º° ½° CPU: ²µ¼µ½½¾ ¾»¾¶¸µ ¶»µ ¾½¾²µ ¿¾²µº¸ ¸ ¿¾²¾¸µ ·°´° ¿¾·¶µ."
            )
        if metrics["memory_percent"] >= memory_threshold:
            recommendations.append(
                "¸·º¸¹ ·°¿° ¿°¼¸: ¿¾²µµ ¿¸»¾¶µ½¸  ²¾º¸¼ ¿¾µ±»µ½¸µ¼ RAM ¸ ¼µ½¸µ ¾´½¾²µ¼µ½½ ½°³·º."
            )
        if metrics["active_processes"] and metrics["active_processes"] > 200:
            recommendations.append(
                " ¸µ¼µ ¼½¾³¾ °º¸²½ ¿¾µ¾²: ½¸·µ º¾»¸µ²¾ ¾½¾² ·°´° ¸ ¾±½¾²»µ½¸¹."
            )

        return {
            "status": "ok",
            "metrics": metrics,
            "recommendations": recommendations,
        }


class CacheOptimizationAgent:
    """Cache repetitive values for a short TTL to reduce repeated work."""

    def __init__(self, brain):
        self.brain = brain
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get_cache_key(self, prefix: str, payload: str) -> str:
        return f"{prefix}:{payload.lower().strip()}"

    def get_or_compute(self, key: str, callback: Callable[[], Any], ttl_seconds: float | None = None):
        ttl = ttl_seconds if ttl_seconds is not None else self.brain.config.get("optimization.cache_ttl_seconds", 30)
        now = time.time()
        value = self.cache.get(key)

        if value and (now - value["time"]) < ttl:
            return value["value"]

        computed = callback()
        self.cache[key] = {"time": now, "value": computed}
        return computed

    def get_summary(self) -> Dict:
        return {
            "cache_entries": len(self.cache),
            "ttl_seconds": self.brain.config.get("optimization.cache_ttl_seconds", 30),
        }


class WorkflowOptimizationAgent:
    """Rank likely repeated tasks using previous pattern suggestions."""

    def __init__(self, learning_manager):
        self.learning_manager = learning_manager

    def analyze(self) -> Dict:
        recognizer = self.learning_manager.pattern_recognizer
        suggestions = recognizer.get_suggestions() if recognizer else []
        top = []

        for item in suggestions:
            if not isinstance(item, dict):
                continue
            if item.get("action"):
                top.append({
                    "type": item.get("type", "unknown"),
                    "action": item.get("action"),
                    "suggestion": item.get("suggestion"),
                    "count": item.get("count", 0),
                })

        return {
            "status": "ok" if recognizer else "unavailable",
            "suggestions": top,
            "recommendations": [
                item.get("suggestion", "")
                for item in top
                if item.get("suggestion")
            ],
        }


class SchedulingOptimizationAgent:
    """Suggest task prioritization based on frequency and urgency."""

    def __init__(self, brain):
        self.brain = brain

    def analyze(self) -> Dict:
        scheduler = getattr(self.brain, "scheduler", None)
        tasks = scheduler.list_tasks() if scheduler else []
        task_payload = []

        for task in tasks:
            task_payload.append({
                "name": task.get("name"),
                "days": task.get("days", []),
                "time": task.get("time"),
                "callback": task.get("callback"),
            })

        return {
            "status": "ok" if scheduler else "unavailable",
            "task_count": len(task_payload),
            "tasks": task_payload,
            "recommendations": [
                "¾²µµ ¿¾²¾¸µ ¾½¾²µ ·°´°¸ ¸ ¾±µ´¸½¸µ ¸, µ»¸ ¾½¸ ´±»¸ ´³ ´³°."
            ] if task_payload else [],
        }


class OptimizationManager:
    """Coordinate all optimization agents; no automatic execution by default."""

    def __init__(self, brain, learning_manager):
        self.brain = brain
        self.learning_manager = learning_manager
        self.resource_agent = ResourceOptimizationAgent(brain)
        self.cache_agent = CacheOptimizationAgent(brain)
        self.workflow_agent = WorkflowOptimizationAgent(learning_manager)
        self.scheduler_agent = SchedulingOptimizationAgent(brain)

    def analyze(self) -> Dict:
        resource = self.resource_agent.analyze()
        workflow = self.workflow_agent.analyze()
        scheduler = self.scheduler_agent.analyze()
        recommendations = (
            resource.get("recommendations", [])
            + workflow.get("recommendations", [])
            + scheduler.get("recommendations", [])
        )

        max_recommendations = int(self.brain.config.get("optimization.max_recommendations", 3))
        recommendations = recommendations[:max(0, max_recommendations)]

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "resource": resource,
                "workflow": workflow,
                "scheduler": scheduler,
                "cache": self.cache_agent.get_summary(),
            },
            "recommendations": recommendations,
            "automatic_actions": False,
        }

    def get_or_compute(self, key: str, callback: Callable[[], Any], ttl_seconds: float | None = None):
        return self.cache_agent.get_or_compute(key, callback, ttl_seconds)

