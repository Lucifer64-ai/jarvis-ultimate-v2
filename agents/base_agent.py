"""
JARVIS - Base Agent Class
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all JARVIS agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.capabilities: List[str] = []
        self.task_history: List[Dict] = []
        self.is_active = False

    @abstractmethod
    def execute_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def can_handle(self, task: str) -> bool:
        pass

    def log_task(self, task: str, result: Dict[str, Any]):
        self.task_history.append({
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        })

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "capabilities": self.capabilities,
            "tasks_completed": len(self.task_history)
        }
