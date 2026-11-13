"""
¦µ½°»¸·¾²°½½¾µ ¿°²»µ½¸µ º¾½¸³°¸µ¹ JARVIS
"""

import os
import json
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv


class Config:
    """µ½µ´¶µ º¾½¸³°¸¸  ¿¾´´µ¶º¾¹ .env °¹»¾²."""

    def __init__(self, config_file: str = "config.json"):
        load_dotenv()
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)

    def get_env_int(self, key: str, default: int = 0) -> int:
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def get_env_bool(self, key: str, default: bool = False) -> bool:
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    @property
    def openai_api_key(self) -> Optional[str]:
        return self.get_env("OPENAI_API_KEY")

    @property
    def openai_model(self) -> str:
        return self.get_env("OPENAI_MODEL", "gpt-4")

    @property
    def openai_max_tokens(self) -> int:
        return self.get_env_int("OPENAI_MAX_TOKENS", 500)

    @property
    def openai_temperature(self) -> float:
        value = self.get_env("OPENAI_TEMPERATURE")
        if value is None:
            return 0.7
        try:
            return float(value)
        except ValueError:
            return 0.7

    @property
    def home_assistant_url(self) -> Optional[str]:
        return self.get_env("HOME_ASSISTANT_URL")

    @property
    def home_assistant_token(self) -> Optional[str]:
        return self.get_env("HOME_ASSISTANT_TOKEN")

    @property
    def mobile_api_host(self) -> str:
        return self.get_env("MOBILE_API_HOST", "0.0.0.0")

    @property
    def mobile_api_port(self) -> int:
        return self.get_env_int("MOBILE_API_PORT", 8080)

    @property
    def mobile_api_secret(self) -> Optional[str]:
        return self.get_env("MOBILE_API_SECRET")

    @property
    def websocket_port(self) -> int:
        return self.get_env_int("WEBSOCKET_PORT", 8765)

    @property
    def log_level(self) -> str:
        return self.get_env("LOG_LEVEL", "INFO")

    @property
    def log_file(self) -> str:
        return self.get_env("LOG_FILE", "jarvis.log")

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def update(self, key: str, value: Any):
        self.config[key] = value
        self.save_config()
