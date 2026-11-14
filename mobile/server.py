"""
API сервер JARVIS для мобильного приложения
"""

import asyncio
import json
import hashlib
import secrets
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

try:
    from aiohttp import web
except ImportError:
    print("Установите: pip install aiohttp")


class MobileServer:
    """HTTP/WebSocket сервер для мобильного приложения."""

    def __init__(self, brain):
        self.brain = brain

        # Чтение из переменных окружения
        self.host = brain.config.mobile_api_host
        self.port = brain.config.mobile_api_port
        self.secret = brain.config.mobile_api_secret

        self.app = web.Application()
        self.tokens: Dict[str, Dict] = {}
        self.tokens_file = Path("data/api_tokens.json")
        self._load_tokens()
        self._setup_routes()

    def _load_tokens(self):
        """Загрузка API токенов."""
        if self.tokens_file.exists():
            with open(self.tokens_file, "r") as f:
                self.tokens = json.load(f)

    def _save_tokens(self):
        """Сохранение токенов."""
        self.tokens_file.parent.mkdir(exist_ok=True)
        with open(self.tokens_file, "w") as f:
            json.dump(self.tokens, f, indent=2)

    def _setup_routes(self):
        """Настройка маршрутов."""
        self.app.router.add_post("/api/auth/login", self.handle_login)
        self.app.router.add_post("/api/auth/register", self.handle_register)
        self.app.router.add_get("/api/status", self.handle_status)
        self.app.router.add_post("/api/command", self.handle_command)
        self.app.router.add_get("/api/system", self.handle_system_info)
        self.app.router.add_get("/api/devices", self.handle_devices)
        self.app.router.add_post("/api/device/control", self.handle_device_control)
        self.app.router.add_get("/api/sensors", self.handle_sensors)
        self.app.router.add_get("/ws", self.websocket_handler)

    def _verify_token(self, request) -> Optional[str]:
        """Проверка токена авторизации."""
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
            if token in self.tokens:
                return self.tokens[token].get("username")
        return None

    async def handle_login(self, request):
        """Авторизация."""
        data = await request.json()
        username = data.get("username")
        password = data.get("password")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        token = secrets.token_hex(32)
        self.tokens[token] = {
            "username": username,
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(days=30)).isoformat()
        }
        self._save_tokens()

        return web.json_response({"token": token, "username": username})

    async def handle_register(self, request):
        """Регистрация нового устройства."""
        data = await request.json()
        device_name = data.get("device_name")

        token = secrets.token_hex(32)
        self.tokens[token] = {
            "device": device_name,
            "created": datetime.now().isoformat(),
            "type": "device"
        }
        self._save_tokens()

        return web.json_response({"token": token, "device": device_name})

    async def handle_status(self, request):
        """Статус JARVIS."""
        user = self._verify_token(request)
        if not user:
            return web.json_response({"error": "Unauthorized"}, status=401)

        status = self.brain.get_status()
        return web.json_response(status)

    async def handle_command(self, request):
        """Выполнение голосовой команды."""
        user = self._verify_token(request)
        if not user:
            return web.json_response({"error": "Unauthorized"}, status=401)

        data = await request.json()
        command = data.get("command", "")

        result = self.brain.execute_command(command)
        return web.json_response(result)

    async def handle_system_info(self, request):
        """Информация о системе."""
        user = self._verify_token(request)
        if not user:
            return web.json_response({"error": "Unauthorized"}, status=401)

        info = self.brain.modules["hardware"].get_full_report()
        return web.json_response(info)

    async def handle_devices(self, request):
        """Список устройств умного дома."""
        user = self._verify_token(request)
        if not user:
            return web.json_response({"error": "Unauthorized"}, status=401)

        if hasattr(self.brain, "smart_home") and "home_assistant" in self.brain.smart_home:
            ha = self.brain.smart_home["home_assistant"]
            devices = await ha.get_states()
            return web.json_response({"devices": devices})

        return web.json_response({"devices": [], "message": "Home Assistant не подключен"})

    async def handle_device_control(self, request):
        """Управление устройством."""
        user = self._verify_token(request)
        if not user:
            return web.json_response({"error": "Unauthorized"}, status=401)

        data = await request.json()
        entity_id = data.get("entity_id")
        action = data.get("action")

        if hasattr(self.brain, "smart_home") and "home_assistant" in self.brain.smart_home:
            ha = self.brain.smart_home["home_assistant"]
            domain = entity_id.split(".")[0]

            if action == "on":
                result = await ha.call_service(domain, "turn_on", entity_id)
            elif action == "off":
                result = await ha.call_service(domain, "turn_off", entity_id)
            elif action == "toggle":
                result = await ha.call_service(domain, "toggle", entity_id)
            else:
                return web.json_response({"error": "Unknown action"}, status=400)

            return web.json_response(result)

        return web.json_response({"error": "Home Assistant not connected"}, status=503)

    async def handle_sensors(self, request):
        """Данные датчиков."""
        user = self._verify_token(request)
        if not user:
            return web.json_response({"error": "Unauthorized"}, status=401)

        if hasattr(self.brain, "smart_home") and "home_assistant" in self.brain.smart_home:
            ha = self.brain.smart_home["home_assistant"]
            states = await ha.get_states()
            sensors = [s for s in states if s["entity_id"].startswith("sensor.")]
            return web.json_response({"sensors": sensors})

        return web.json_response({"sensors": []})

    async def websocket_handler(self, request):
        """WebSocket для real-time обновлений."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)

                if data.get("type") == "command":
                    result = self.brain.execute_command(data.get("command", ""))
                    await ws.send_json({"type": "result", "data": result})

                elif data.get("type") == "status":
                    status = self.brain.get_status()
                    await ws.send_json({"type": "status", "data": status})

            elif msg.type == web.WSMsgType.ERROR:
                self.brain.logger.error(f"WebSocket error: {ws.exception()}")

        return ws

    def start(self):
        """Запуск сервера."""
        self.brain.logger.info(f"Mobile API сервер запущен на {self.host}:{self.port}")
        web.run_app(self.app, host=self.host, port=self.port)

    def start_async(self):
        """Запуск в отдельном потоке."""
        import threading
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
