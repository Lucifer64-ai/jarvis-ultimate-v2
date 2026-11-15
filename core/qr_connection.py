"""
JARVIS QR Connection - Подключение через QR-код
Генерирует QR-код для быстрого подключения с телефона
"""

import qrcode
import json
import uuid
import time
from typing import Dict, Optional
from pathlib import Path


class QRConnectionManager:
    """Менеджер QR-подключения."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Настройки
        self.server_ip = self._get_local_ip()
        self.server_port = 8765
        self.auth_tokens = {}  # token -> {created_at, expires_at, device_name}
        self.qr_codes_dir = Path("assets/qr_codes")
        self.qr_codes_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"QR Connection Manager инициализирован. IP: {self.server_ip}")

    def _get_local_ip(self) -> str:
        """Получение локального IP адреса."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def generate_connection_qr(self, device_name: str = "Mobile") -> Dict:
        """Генерация QR-кода для подключения."""
        try:
            # Генерируем токен авторизации
            token = str(uuid.uuid4())
            expires_at = int(time.time()) + 300  # 5 минут

            # Сохраняем токен
            self.auth_tokens[token] = {
                "created_at": int(time.time()),
                "expires_at": expires_at,
                "device_name": device_name,
                "used": False
            }

            # Формируем данные для QR
            qr_data = {
                "type": "jarvis_connection",
                "version": "1.0",
                "server_ip": self.server_ip,
                "server_port": self.server_port,
                "auth_token": token,
                "expires_at": expires_at,
                "device_name": device_name
            }

            # Генерируем QR-код
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)

            # Сохраняем QR-код
            img = qr.make_image(fill_color="black", back_color="white")
            qr_path = self.qr_codes_dir / f"connection_{token[:8]}.png"
            img.save(qr_path)

            self.logger.info(f"QR-код сгенерирован: {qr_path}")

            return {
                "status": "ok",
                "qr_path": str(qr_path),
                "auth_token": token,
                "expires_at": expires_at,
                "server_url": f"ws://{self.server_ip}:{self.server_port}",
                "message": f"QR-код создан. Действителен 5 минут."
            }

        except Exception as e:
            self.logger.error(f"Ошибка генерации QR: {e}")
            return {
                "status": "error",
                "message": f"Ошибка генерации QR-кода: {str(e)}"
            }

    def validate_token(self, token: str) -> Dict:
        """Проверка токена авторизации."""
        if token not in self.auth_tokens:
            return {"status": "error", "message": "Недействительный токен"}

        token_data = self.auth_tokens[token]

        # Проверяем срок действия
        if time.time() > token_data["expires_at"]:
            return {"status": "error", "message": "Токен истёк"}

        # Проверяем использование
        if token_data["used"]:
            return {"status": "error", "message": "Токен уже использован"}

        # Помечаем как использованный
        token_data["used"] = True

        return {
            "status": "ok",
            "device_name": token_data["device_name"],
            "message": "Авторизация успешна"
        }

    def cleanup_expired_tokens(self):
        """Удаление истёкших токенов."""
        current_time = time.time()
        expired = [
            token for token, data in self.auth_tokens.items()
            if current_time > data["expires_at"]
        ]

        for token in expired:
            del self.auth_tokens[token]
            self.logger.info(f"Удалён истёкший токен: {token[:8]}")

    def get_active_connections(self) -> Dict:
        """Получение списка активных подключений."""
        active = [
            {
                "token": token[:8] + "...",
                "device_name": data["device_name"],
                "created_at": data["created_at"],
                "used": data["used"]
            }
            for token, data in self.auth_tokens.items()
            if not data["used"] and time.time() < data["expires_at"]
        ]

        return {
            "status": "ok",
            "active_connections": active,
            "count": len(active)
        }


def create_qr_connection_manager(brain):
    """Фабричная функция."""
    return QRConnectionManager(brain)
