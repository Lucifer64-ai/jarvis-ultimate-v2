"""
JARVIS LLM Router - Переключатель между OpenAI и локальной LLM
Автоматический выбор модели в зависимости от доступности
"""

import os
from typing import Dict, Optional
from datetime import datetime


class LLMRouter:
    """Маршрутизатор запросов между OpenAI и локальной LLM."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Модули
        self.openai = None
        self.ollama = None

        # Режим работы
        self.mode = "auto"  # auto, openai, ollama
        self.current_provider = None

        # Инициализация
        self._init_modules()

    def _init_modules(self):
        """Инициализация модулей LLM."""
        # OpenAI
        try:
            from ai.chatgpt_integration import ChatGPTIntegration
            self.openai = ChatGPTIntegration(self.brain)
            self.logger.info("OpenAI модуль инициализирован")
        except Exception as e:
            self.logger.warning(f"OpenAI недоступен: {e}")
            self.openai = None

        # Ollama
        try:
            from ai.ollama_integration import OllamaIntegration
            self.ollama = OllamaIntegration(self.brain)
            self.logger.info("Ollama модуль инициализирован")
        except Exception as e:
            self.logger.warning(f"Ollama недоступен: {e}")
            self.ollama = None

    def chat(self, message: str, context: str = "") -> Dict:
        """Отправка запроса с автоматическим выбором провайдера."""

        # Принудительный режим
        if self.mode == "openai":
            if self.openai:
                return self.openai.chat(message, context)
            else:
                return {"status": "error", "message": "OpenAI недоступен"}

        elif self.mode == "ollama":
            if self.ollama and self.ollama.is_available:
                return self.ollama.chat(message, context)
            else:
                return {"status": "error", "message": "Ollama недоступен"}

        # Автоматический режим
        else:
            # Приоритет: OpenAI -> Ollama
            if self.openai and self._check_openai_key():
                self.current_provider = "openai"
                result = self.openai.chat(message, context)
                if result.get("status") == "ok":
                    return result

            # Fallback на Ollama
            if self.ollama and self.ollama.is_available:
                self.current_provider = "ollama"
                return self.ollama.chat(message, context)

            # Оба недоступны
            return {
                "status": "error",
                "message": "Нет доступных LLM. Установите OpenAI API ключ или Ollama."
            }

    def _check_openai_key(self) -> bool:
        """Проверка наличия OpenAI API ключа."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        return bool(api_key and api_key != "your_api_key_here")

    def set_mode(self, mode: str) -> Dict:
        """Установка режима работы."""
        valid_modes = ["auto", "openai", "ollama"]

        if mode not in valid_modes:
            return {
                "status": "error",
                "message": f"Недопустимый режим. Доступны: {', '.join(valid_modes)}"
            }

        self.mode = mode
        self.logger.info(f"Режим LLM изменён на: {mode}")

        return {
            "status": "ok",
            "message": f"Режим изменён на {mode}",
            "mode": mode
        }

    def get_status(self) -> Dict:
        """Получение статуса системы."""
        return {
            "status": "ok",
            "mode": self.mode,
            "current_provider": self.current_provider,
            "openai_available": self.openai is not None and self._check_openai_key(),
            "ollama_available": self.ollama is not None and self.ollama.is_available if self.ollama else False
        }

    def list_providers(self) -> Dict:
        """Список доступных провайдеров."""
        providers = []

        if self.openai and self._check_openai_key():
            providers.append({
                "name": "openai",
                "status": "available",
                "model": self.openai.model
            })

        if self.ollama and self.ollama.is_available:
            providers.append({
                "name": "ollama",
                "status": "available",
                "model": self.ollama.model,
                "models": self.ollama.available_models
            })

        return {
            "status": "ok",
            "providers": providers,
            "current_mode": self.mode
        }


def create_llm_router(brain):
    """Фабричная функция для создания маршрутизатора."""
    return LLMRouter(brain)
