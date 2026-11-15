"""
JARVIS Sub-Agent Orchestration
Управление подзадачами через других агентов
"""

import threading
import queue
import time
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class SubAgent:
    """Подзадача для выполнения"""
    id: str
    name: str
    task: str
    handler: Callable
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Dict] = None
    error: Optional[str] = None
    thread: Optional[threading.Thread] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class SubAgentOrchestrator:
    """Оркестратор подзадач"""

    def __init__(self):
        self.agents: Dict[str, SubAgent] = {}
        self.result_queue = queue.Queue()
        self.max_concurrent = 5

    def create_agent(self, name: str, task: str, handler: Callable) -> str:
        """Создание нового подзадача"""
        agent_id = f"agent_{int(time.time() * 1000)}"

        agent = SubAgent(
            id=agent_id,
            name=name,
            task=task,
            handler=handler
        )

        self.agents[agent_id] = agent
        print(f"✅ Создан подзадач: {name} ({agent_id})")

        return agent_id

    def start_agent(self, agent_id: str) -> bool:
        """Запуск подзадача"""
        if agent_id not in self.agents:
            print(f"❌ Подзадач не найден: {agent_id}")
            return False

        agent = self.agents[agent_id]

        if agent.status != AgentStatus.IDLE:
            print(f"⚠️ Подзадач уже запущен или завершён")
            return False

        running_count = sum(1 for a in self.agents.values() if a.status == AgentStatus.RUNNING)
        if running_count >= self.max_concurrent:
            print(f"⚠️ Достигнут лимит одновременных задач ({self.max_concurrent})")
            return False

        agent.status = AgentStatus.RUNNING
        agent.start_time = time.time()

        agent.thread = threading.Thread(
            target=self._run_agent,
            args=(agent,),
            daemon=True
        )
        agent.thread.start()

        print(f"🚀 Запущен подзадач: {agent.name}")
        return True

    def _run_agent(self, agent: SubAgent):
        """Внутренний метод выполнения подзадача"""
        try:
            result = agent.handler(agent.task)
            agent.result = result
            agent.status = AgentStatus.COMPLETED
            agent.end_time = time.time()

            self.result_queue.put({
                'agent_id': agent.id,
                'status': 'completed',
                'result': result
            })

            print(f"✅ Подзадач завершён: {agent.name}")

        except Exception as e:
            agent.error = str(e)
            agent.status = AgentStatus.FAILED
            agent.end_time = time.time()

            self.result_queue.put({
                'agent_id': agent.id,
                'status': 'failed',
                'error': str(e)
            })

            print(f"❌ Подзадач провален: {agent.name} - {e}")

    def cancel_agent(self, agent_id: str) -> bool:
        """Отмена подзадача"""
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]

        if agent.status == AgentStatus.RUNNING:
            agent.status = AgentStatus.CANCELLED
            agent.end_time = time.time()
            print(f"🛑 Подзадач отменён: {agent.name}")
            return True

        return False

    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Получение статуса подзадача"""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]

        return {
            'id': agent.id,
            'name': agent.name,
            'task': agent.task,
            'status': agent.status.value,
            'result': agent.result,
            'error': agent.error,
            'duration': (agent.end_time - agent.start_time) if agent.end_time and agent.start_time else None
        }

    def get_all_agents(self) -> List[Dict]:
        """Получение списка всех подзадач"""
        return [self.get_agent_status(agent_id) for agent_id in self.agents.keys()]

    def wait_for_completion(self, agent_id: str, timeout: Optional[float] = None) -> Optional[Dict]:
        """Ожидание завершения подзадача"""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]

        if agent.thread:
            agent.thread.join(timeout=timeout)

        return self.get_agent_status(agent_id)
