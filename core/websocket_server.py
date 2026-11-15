"""
JARVIS WebSocket Server - Сервер для мобильного приложения
Принимает подключения с телефона через QR-код
"""

import asyncio
import json
import websockets
from typing import Dict, Set
from datetime import datetime


class JarvisWebSocketServer:
    """WebSocket сервер для связи с мобильным приложением."""

    def __init__(self, brain, host="0.0.0.0", port=8765):
        self.brain = brain
        self.logger = brain.logger
        self.host = host
        self.port = port

        # Подключённые клиенты
        self.connected_clients: Set = set()
        self.client_info: Dict = {}  # websocket -> {device_name, connected_at}

        # Сервер
        self.server = None
        self.running = False

        self.logger.info(f"WebSocket сервер инициализирован: {host}:{port}")

    async def start(self):
        """Запуск WebSocket сервера."""
        try:
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            self.running = True
            self.logger.info(f"✅ WebSocket сервер запущен на {self.host}:{self.port}")

            # Держим сервер запущенным
            await self.server.wait_closed()

        except Exception as e:
            self.logger.error(f"Ошибка запуска WebSocket сервера: {e}")
            self.running = False

    async def stop(self):
        """Остановка сервера."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.running = False
            self.logger.info("WebSocket сервер остановлен")

    async def handle_client(self, websocket, path):
        """Обработка подключений клиентов."""
        client_address = websocket.remote_address
        self.logger.info(f"📱 Новое подключение от {client_address}")

        self.connected_clients.add(websocket)
        self.client_info[websocket] = {
            "device_name": "Unknown",
            "connected_at": datetime.now().isoformat()
        }

        try:
            # Отправляем приветствие
            await websocket.send(json.dumps({
                "type": "welcome",
                "message": "Добро пожаловать в JARVIS!",
                "timestamp": datetime.now().isoformat()
            }))

            # Слушаем сообщения
            async for message in websocket:
                await self.process_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"📱 Клиент {client_address} отключился")
        except Exception as e:
            self.logger.error(f"Ошибка обработки клиента: {e}")
        finally:
            self.connected_clients.remove(websocket)
            del self.client_info[websocket]

    async def process_message(self, websocket, message):
        """Обработка входящего сообщения."""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            self.logger.info(f"📨 Получено сообщение: {msg_type}")

            if msg_type == "auth":
                # Авторизация через токен
                token = data.get("token")
                result = self.brain.qr_connection.validate_token(token)

                if result["status"] == "ok":
                    self.client_info[websocket]["device_name"] = result["device_name"]
                    self.client_info[websocket]["authenticated"] = True

                    await websocket.send(json.dumps({
                        "type": "auth_success",
                        "message": "Авторизация успешна"
                    }))
                else:
                    await websocket.send(json.dumps({
                        "type": "auth_error",
                        "message": result["message"]
                    }))

            elif msg_type == "command":
                # Выполнение команды
                if not self.client_info[websocket].get("authenticated"):
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Требуется авторизация"
                    }))
                    return

                command_text = data.get("text", "")
                self.logger.info(f"🎯 Команда от мобильного: {command_text}")

                # Выполняем команду через brain
                result = self.brain.process_command(command_text)

                await websocket.send(json.dumps({
                    "type": "command_result",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }))

            elif msg_type == "get_status":
                # Получение статуса системы
                import psutil

                status = {
                    "cpu": psutil.cpu_percent(),
                    "ram": psutil.virtual_memory().percent,
                    "network": self._get_network_speed(),
                    "uptime": self._get_uptime(),
                    "processes": len(psutil.pids())
                }

                await websocket.send(json.dumps({
                    "type": "status",
                    "data": status,
                    "timestamp": datetime.now().isoformat()
                }))

            elif msg_type == "get_logs":
                # Получение логов
                logs = self._get_recent_logs()

                await websocket.send(json.dumps({
                    "type": "logs_history",
                    "logs": logs
                }))

            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Неизвестный тип сообщения: {msg_type}"
                }))

        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Неверный формат JSON"
            }))
        except Exception as e:
            self.logger.error(f"Ошибка обработки сообщения: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))

    def _get_network_speed(self) -> str:
        """Получение скорости сети."""
        try:
            import speedtest
            st = speedtest.Speedtest()
            download = st.download() / 1_000_000  # Mbps
            return f"{download:.1f} Mbps"
        except Exception:
            return "N/A"

    def _get_uptime(self) -> str:
        """Получение времени работы системы."""
        import psutil
        boot_time = psutil.boot_time()
        uptime_seconds = int(datetime.now().timestamp() - boot_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def _get_recent_logs(self, limit=50) -> list:
        """Получение последних логов."""
        # Здесь должна быть реальная реализация получения логов
        return []

    async def broadcast(self, message: dict):
        """Отправка сообщения всем подключённым клиентам."""
        if self.connected_clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.connected_clients],
                return_exceptions=True
            )


def create_websocket_server(brain, host="0.0.0.0", port=8765):
    """Фабричная функция."""
    return JarvisWebSocketServer(brain, host, port)
