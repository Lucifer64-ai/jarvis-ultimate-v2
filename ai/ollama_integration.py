"""
JARVIS Ollama Integration
Local LLM support with automatic fallback
"""

import os
import json
import subprocess
import requests
from typing import Dict, List, Optional
from datetime import datetime


class OllamaIntegration:
    """Интеграция с локальной LLM через Ollama."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Настройки
        self.base_url = "http://localhost:11434"
        self.model = "llama3.2"  # По умолчанию
        self.available_models = []

        # Контекст разговора
        self.conversation_history: List[Dict] = []
        self.max_history = 20

        # Статус
        self.is_available = False

        # Инициализация
        self._check_ollama()

    def _check_ollama(self) -> bool:
        """Проверка доступности Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [m['name'] for m in data.get('models', [])]
                self.is_available = True
                self.logger.info(f"Ollama доступен. Модели: {', '.join(self.available_models)}")
                return True
            else:
                self.is_available = False
                return False
        except Exception as e:
            self.logger.warning(f"Ollama недоступен: {e}")
            self.is_available = False
            return False

    def chat(self, message: str, context: str = "") -> Dict:
        """Отправить сообщение в локальную LLM."""
        if not self.is_available:
            if not self._check_ollama():
                return {
                    "status": "error",
                    "message": "Ollama не запущен. Установите и запустите Ollama."
                }

        try:
            # Добавляем в историю
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })

            # Ограничиваем историю
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]

            # Формируем промпт
            prompt = self._build_prompt(message, context)

            # Запрос к Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "context": []
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                assistant_message = result.get('response', '')

                # Добавляем ответ в историю
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "timestamp": datetime.now().isoformat()
                })

                self.logger.info(f"Ollama ответ: {assistant_message[:100]}...")

                return {
                    "status": "ok",
                    "message": assistant_message,
                    "model": self.model,
                    "source": "local"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка Ollama: {response.status_code}"
                }

        except Exception as e:
            self.logger.error(f"Ошибка Ollama: {e}")
            return {
                "status": "error",
                "message": f"Ошибка обращения к Ollama: {str(e)}"
            }

    def _build_prompt(self, message: str, context: str = "") -> str:
        """Построение промпта с контекстом."""
        system_prompt = """Ты - JARVIS, продвинутый ИИ-ассистент. 
Отвечай на русском языке, вежливо и профессионально.
Будь краток и по существу."""

        # Добавляем историю
        history_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in self.conversation_history[-10:]
        ])

        prompt = f"""{system_prompt}

ИСТОРИЯ ДИАЛОГА:
{history_text}

КОНТЕКСТ: {context if context else "Общий диалог"}

ПОЛЬЗОВАТЕЛЬ: {message}
JARVIS:"""

        return prompt

    def set_model(self, model: str) -> Dict:
        """Установить модель Ollama."""
        if not self.is_available:
            return {"status": "error", "message": "Ollama недоступен"}

        if model in self.available_models:
            self.model = model
            self.logger.info(f"Модель Ollama изменена на {model}")
            return {"status": "ok", "message": f"Модель изменена на {model}"}
        else:
            return {
                "status": "error",
                "message": f"Модель {model} не найдена. Доступны: {', '.join(self.available_models)}"
            }

    def list_models(self) -> Dict:
        """Список доступных моделей."""
        if not self.is_available:
            return {"status": "error", "message": "Ollama недоступен"}

        return {
            "status": "ok",
            "models": self.available_models,
            "current": self.model
        }

    def clear_history(self) -> Dict:
        """Очистить историю разговора."""
        self.conversation_history = []
        self.logger.info("История Ollama очищена")
        return {"status": "ok", "message": "История очищена"}

    def get_status(self) -> Dict:
        """Получить статус интеграции."""
        return {
            "status": "ok",
            "available": self.is_available,
            "model": self.model,
            "available_models": self.available_models,
            "history_count": len(self.conversation_history)
        }


def create_ollama_module(brain):
    """Фабричная функция для создания модуля Ollama."""
    return OllamaIntegration(brain)
