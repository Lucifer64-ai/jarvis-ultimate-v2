"""
Локальная языковая модель JARVIS (Ollama интеграция)
"""

import requests
import json
from typing import Dict, List, Optional
import logging


class LocalLLM:
    """Интеграция с локальной языковой моделью через Ollama."""

    def __init__(self, brain):
        self.brain = brain
        self.ollama_url = brain.config.get("local_llm", {}).get("ollama_url", "http://localhost:11434")
        self.model = brain.config.get("local_llm", {}).get("model", "llama3.2")
        self.enabled = brain.config.get("local_llm", {}).get("enabled", False)

        if self.enabled:
            self.brain.logger.info(f"Локальная LLM включена: {self.model} через {self.ollama_url}")
        else:
            self.brain.logger.info("Локальная LLM отключена")

    def is_available(self) -> bool:
        """Проверка доступности Ollama."""
        if not self.enabled:
            return False

        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> List[str]:
        """Список доступных моделей."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            self.brain.logger.error(f"Ошибка получения списка моделей: {e}")

        return []

    def generate(self, prompt: str, system: str = None) -> Dict:
        """Генерация ответа."""
        if not self.is_available():
            return {
                "status": "error",
                "message": "Ollama недоступна. Установка на https://ollama.ai"
            }

        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }

            if system:
                payload["system"] = system

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "ok",
                    "response": data.get("response", ""),
                    "model": self.model,
                    "done": data.get("done", False)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка Ollama: {response.status_code}"
                }

        except requests.exceptions.Timeout:
            return {"status": "error", "message": "Таймаут запроса к Ollama"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def chat(self, messages: List[Dict]) -> Dict:
        """Чат с моделью."""
        if not self.is_available():
            return {
                "status": "error",
                "message": "Ollama недоступна"
            }

        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False
            }

            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                message = data.get("message", {})
                return {
                    "status": "ok",
                    "response": message.get("content", ""),
                    "role": message.get("role", "assistant"),
                    "model": self.model
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка Ollama: {response.status_code}"
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def set_model(self, model: str) -> Dict:
        """Установка модели."""
        available = self.list_models()

        if model not in available:
            return {
                "status": "error",
                "message": f"Модель '{model}' недоступна. Доступные: {', '.join(available)}"
            }

        self.model = model
        self.brain.config.set("local_llm.model", model)

        return {
            "status": "ok",
            "message": f"Модель установлена: {model}"
        }

    def enable(self) -> Dict:
        """Включение локальной LLM."""
        self.enabled = True
        self.brain.config.set("local_llm.enabled", True)
        return {"status": "ok", "message": "Локальная LLM включена"}

    def disable(self) -> Dict:
        """Отключение локальной LLM."""
        self.enabled = False
        self.brain.config.set("local_llm.enabled", False)
        return {"status": "ok", "message": "Локальная LLM отключена"}

    def get_status(self) -> Dict:
        """Статус локальной LLM."""
        return {
            "enabled": self.enabled,
            "available": self.is_available(),
            "model": self.model,
            "ollama_url": self.ollama_url,
            "available_models": self.list_models() if self.is_available() else []
        }
