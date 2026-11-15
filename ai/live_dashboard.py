"""
JARVIS Live Dashboard Module
Веб-панель мониторинга в реальном времени
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
import psutil
import time
from typing import Dict, List
from collections import deque

class LiveDashboard:
    """Веб-панель мониторинга JARVIS"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.active_connections: List[WebSocket] = []
        self.metrics_history = deque(maxlen=100)
        self.jarvis_status = {
            "status": "active",
            "uptime": 0,
            "commands_processed": 0,
            "agents_running": 0,
            "last_command": None,
            "start_time": time.time()
        }

        self._setup_routes()

    def _setup_routes(self):
        """Настройка маршрутов FastAPI"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            return self._generate_html()

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            try:
                while True:
                    # Отправляем метрики каждые 1 секунду
                    metrics = self._collect_metrics()
                    await websocket.send_json(metrics)
                    await asyncio.sleep(1)
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)

        @self.app.get("/api/metrics")
        async def get_metrics():
            return self._collect_metrics()

        @self.app.get("/api/status")
        async def get_status():
            return self.jarvis_status

    def _collect_metrics(self) -> Dict:
        """Сборка системных метрик"""
        metrics = {
            "timestamp": time.time(),
            "cpu": psutil.cpu_percent(interval=0.1),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "network": {
                "sent": psutil.net_io_counters().bytes_sent,
                "recv": psutil.net_io_counters().bytes_recv
            },
            "jarvis": self.jarvis_status
        }

        self.metrics_history.append(metrics)
        return metrics

    def _generate_html(self) -> str:
        """Генерация HTML дашборда"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>JARVIS Dashboard</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff00;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            text-shadow: 0 0 10px #00ff00;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .metric-card {
            background: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
        }
        .metric-label {
            text-align: center;
            opacity: 0.7;
            margin-top: 10px;
        }
        .status {
            text-align: center;
            font-size: 1.5em;
            margin: 20px 0;
        }
        .log {
            background: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 JARVIS DASHBOARD</h1>

        <div class="status" id="status">
            Статус: <span id="jarvis-status">Загрузка...</span>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value" id="cpu">0%</div>
                <div class="metric-label">CPU</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="memory">0%</div>
                <div class="metric-label">RAM</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="disk">0%</div>
                <div class="metric-label">DISK</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="commands">0</div>
                <div class="metric-label">COMMANDS</div>
            </div>
        </div>

        <div class="log" id="log">
            <h3>📋 Activity Log</h3>
            <div id="log-entries"></div>
        </div>
    </div>

    <script>
        const ws = new WebSocket('ws://' + window.location.host + '/ws');

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);

            document.getElementById('cpu').textContent = data.cpu.toFixed(1) + '%';
            document.getElementById('memory').textContent = data.memory.toFixed(1) + '%';
            document.getElementById('disk').textContent = data.disk.toFixed(1) + '%';
            document.getElementById('commands').textContent = data.jarvis.commands_processed;
            document.getElementById('jarvis-status').textContent = data.jarvis.status;
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    </script>
</body>
</html>
"""

    def update_status(self, **kwargs):
        """Обновление статуса JARVIS"""
        self.jarvis_status.update(kwargs)

    def log_command(self, command: str, result: str):
        """Логирование команды"""
        self.jarvis_status["commands_processed"] += 1
        self.jarvis_status["last_command"] = {
            "command": command,
            "result": result,
            "timestamp": time.time()
        }

    def start(self):
        """Запуск сервера"""
        import uvicorn
        print(f"🌐 Dashboard запущен: http://{self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")

# Пример использования
if __name__ == "__main__":
    dashboard = LiveDashboard()
    dashboard.start()
