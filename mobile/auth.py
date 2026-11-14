"""
Аутентификация для мобильного API
"""

import hashlib
import secrets
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta


class AuthManager:
    """Голосовые аутентификации."""

    def __init__(self, brain):
        self.brain = brain
        self.users_file = Path("data/users.json")
        self.tokens_file = Path("data/api_tokens.json")
        self.users_file.parent.mkdir(exist_ok=True)

        self.users: Dict = self._load_users()
        self.tokens: Dict = self._load_tokens()

    def _load_users(self) -> Dict:
        """Загрузка пользователей."""
        if self.users_file.exists():
            with open(self.users_file, "r") as f:
                return json.load(f)
        return {}

    def _save_users(self):
        """Сохранение пользователей."""
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=2)

    def _load_tokens(self) -> Dict:
        """Загрузка токенов."""
        if self.tokens_file.exists():
            with open(self.tokens_file, "r") as f:
                return json.load(f)
        return {}

    def _save_tokens(self):
        """Сохранение токенов."""
        with open(self.tokens_file, "w") as f:
            json.dump(self.tokens, f, indent=2)

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> Dict:
        """Регистрация нового пользователя."""
        if username in self.users:
            return {"status": "error", "message": "Пользователь уже существует"}

        self.users[username] = {
            "password_hash": self._hash_password(password),
            "created": datetime.now().isoformat()
        }
        self._save_users()

        return {"status": "ok", "username": username}

    def authenticate(self, username: str, password: str) -> Dict:
        """Аутентификация пользователя."""
        if username not in self.users:
            return {"status": "error", "message": "Пользователь не найден"}

        user = self.users[username]
        if user["password_hash"] != self._hash_password(password):
            return {"status": "error", "message": "Неверный пароль"}

        # Генерация токена
        token = secrets.token_hex(32)
        self.tokens[token] = {
            "username": username,
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(days=30)).isoformat()
        }
        self._save_tokens()

        return {"status": "ok", "token": token, "username": username}

    def verify_token(self, token: str) -> Optional[str]:
        """Проверка токена."""
        if token not in self.tokens:
            return None

        token_data = self.tokens[token]
        expires = datetime.fromisoformat(token_data["expires"])

        if datetime.now() > expires:
            del self.tokens[token]
            self._save_tokens()
            return None

        return token_data.get("username")

    def revoke_token(self, token: str) -> Dict:
        """Отзыв токена."""
        if token in self.tokens:
            del self.tokens[token]
            self._save_tokens()
            return {"status": "ok"}
        return {"status": "error", "message": "Токен не найден"}

    def list_users(self) -> list:
        """Список пользователей."""
        return list(self.users.keys())

    def delete_user(self, username: str) -> Dict:
        """Удаление пользователя."""
        if username in self.users:
            del self.users[username]
            self._save_users()
            return {"status": "ok"}
        return {"status": "error", "message": "Пользователь не найден"}
