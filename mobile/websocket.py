"""
WebSocket сервер JARVIS для real-time обновлений
"""

import asyncio
import json
import websockets
from typing import Set, Dict
import threading


class WebSocketServer:
    """WebSocket сервер для real-time связи."""

    def __init__(self, brain):
        self.brain = brain
        self.port = brain.config.websocket_port
        self.clients: Set = set()
        self.running = False

    async def handler(self, websocket, path):
        """Обработка WebSocket подключений."""
        self.clients.add(websocket)
        self.brain.logger.info(f"Новое WebSocket подключение. Всего клиентов: {len(self.clients)}")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"error": "Invalid JSON"}))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            self.brain.logger.info(f"Клиент отключён. Всего клиентов: {len(self.clients)}")

    async def _process_message(self, websocket, data: Dict):
        """Обработка входящего сообщения."""
        msg_type = data.get("type")

        if msg_type == "command":
            command = data.get("command", "")
            result = self.brain.execute_command(command)
            await websocket.send(json.dumps({
                "type": "command_result",
                "data": result
            }))

        elif msg_type == "status":
            status = self.brain.get_status()
            await websocket.send(json.dumps({
                "type": "status",
                "data": status
            }))

        elif msg_type == "subscribe":
            # Подписка на обновления
            await websocket.send(json.dumps({
                "type": "subscribed",
                "message": "Подписка на обновления активирована"
            }))

    async def broadcast(self, message: Dict):
        """Отправка сообщения всем подключённым клиентам."""
        if self.clients:
            await asyncio.wait([
                client.send(json.dumps(message))
                for client in self.clients
            ])

    async def start_server(self):
        """Запуск WebSocket сервера."""
        self.running = True
        server = await websockets.serve(self.handler, "0.0.0.0", self.port)
        self.brain.logger.info(f"WebSocket сервер запущен на порту {self.port}")
        await server.wait_closed()

    def start(self):
        """Запуск в отдельном потоке."""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start_server())

        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()

    def stop(self):
        """Остановка сервера."""
        self.running = False
