"""
µ½¸¸º°¸ для ¼¾±¸»½¾³¾ API
"""

import hashlib
import secrets
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta


class AuthManager:
    """голосовые °µ½¸¸º°¸µ¹."""

    def __init__(self, brain):
        self.brain = brain
        self.users_file = Path("data/users.json")
        self.tokens_file = Path("data/api_tokens.json")
        self.users_file.parent.mkdir(exist_ok=True)
        
        self.users: Dict = self._load_users()
        self.tokens: Dict = self._load_tokens()

    def _load_users(self) -> Dict:
        """°³·º° ¿¾»·¾²°µ»µ¹."""
        if self.users_file.exists():
            with open(self.users_file, "r") as f:
                return json.load(f)
        return {}

    def _save_users(self):
        """¡¾°ни½¸µ ¿¾»·¾²°µ»µ¹."""
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=2)

    def _load_tokens(self) -> Dict:
        """°³·º° ¾ºµ½¾²."""
        if self.tokens_file.exists():
            with open(self.tokens_file, "r") as f:
                return json.load(f)
        return {}

    def _save_tokens(self):
        """¡¾°ни½¸µ ¾ºµ½¾²."""
        with open(self.tokens_file, "w") as f:
            json.dump(self.tokens, f, indent=2)

    def _hash_password(self, password: str) -> str:
        """¥µ¸¾²°½¸µ ¿°¾»."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> Dict:
        """ µ³¸°¸ ½¾²¾³¾ ¿¾»·¾²°µ»."""
        if username in self.users:
            return {"status": "error", "message": "¾»·¾²°µ» ¶µ µ²µ"}
        
        self.users[username] = {
            "password_hash": self._hash_password(password),
            "created": datetime.now().isoformat()
        }
        self._save_users()
        
        return {"status": "ok", "username": username}

    def authenticate(self, username: str, password: str) -> Dict:
        """µ½¸¸º°¸ ¿¾»·¾²°µ»."""
        if username not in self.users:
            return {"status": "error", "message": "¾»·¾²°µ» ни на¹´µ½"}
        
        user = self.users[username]
        if user["password_hash"] != self._hash_password(password):
            return {"status": "error", "message": "µ²µ½¹ ¿°¾»"}
        
        # µни°¸ ¾ºµна
        token = secrets.token_hex(32)
        self.tokens[token] = {
            "username": username,
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(days=30)).isoformat()
        }
        self._save_tokens()
        
        return {"status": "ok", "token": token, "username": username}

    def verify_token(self, token: str) -> Optional[str]:
        """¾²µº° ¾ºµна."""
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
        """·² ¾ºµна."""
        if token in self.tokens:
            del self.tokens[token]
            self._save_tokens()
            return {"status": "ok"}
        return {"status": "error", "message": "¢¾ºµ½ ни на¹´µ½"}

    def list_users(self) -> list:
        """¡¿¸¾º ¿¾»·¾²°µ»µ¹."""
        return list(self.users.keys())

    def delete_user(self, username: str) -> Dict:
        """£´°»µ½¸µ ¿¾»·¾²°µ»."""
        if username in self.users:
            del self.users[username]
            self._save_users()
            return {"status": "ok"}
        return {"status": "error", "message": "¾»·¾²°µ» ни на¹´µ½"}
