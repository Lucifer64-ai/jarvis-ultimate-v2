"""
JARVIS LLM Router - Переключатель между OpenAI и локальной LLM
Автоматический выбор модели в зависимости от доступности и сети
"""

import os
import socket
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

        # Сетевой статус (кешируется на 30 секунд)
        self._network_cached = None
        self._network_cache_time = 0
        self._network_cache_ttl = 30

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

    # === СЕТЕВОЕ ОБНАРУЖЕНИЕ ===

    def _check_network(self) -> bool:
        """Проверка доступности интернет-соединения (кешируется 30 сек)."""
        import time
        now = time.time()

        # Возвращаем кеш, если ещё актуален
        if self._network_cached is not None and (now - self._network_cache_time) < self._network_cache_ttl:
            return self._network_cached

        # Проверяем DNS и TCP соединение к известному хосту (Google DNS)
        result = False
        try:
            # Пытаемся разрешить и подключиться к 8.8.8.8:53 (DNS)
            socket.setdefaulttimeout(3)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("8.8.8.8", 53))
            sock.close()
            result = True
        except Exception:
            try:
                # Fallback: проверяем через DNS разрешение домена
                socket.gethostbyname("api.openai.com")
                result = True
            except Exception:
                result = False

        self._network_cached = result
        self._network_cache_time = now
        return result

    def is_network_available(self) -> bool:
        """Публичный метод проверки сети."""
        return self._check_network()

    # === ЧАТ ===

    def chat(self, message: str, context: str = "") -> Dict:
        """Отправка запроса с автоматическим выбором провайдера по сети."""

        # Принудительный режим openai
        if self.mode == "openai":
            if self.openai:
                return self.openai.chat(message, context)
            else:
                return {"status": "error", "message": "OpenAI недоступен (режим принудительно открыт)"}

        # Принудительный режим ollama
        elif self.mode == "ollama":
            if self.ollama and self.ollama.is_available:
                return self.ollama.chat(message, context)
            else:
                return {"status": "error", "message": "Ollama недоступен (режим принудительно открыт)"}

        # Автоматический режим: сеть есть -> OpenAI, сети нет -> Ollama
        else:
            network = self._check_network()

            # ---- Есть интернет: приоритет OpenAI ----
            if network:
                if self.openai and self._check_openai_key():
                    self.current_provider = "openai"
                    result = self.openai.chat(message, context)
                    if result.get("status") == "ok":
                        self.logger.info("LLM: сеть доступна, используется OpenAI")
                        return result
                    # OpenAI вернул ошибку — пробуем Ollama как фолбэк
                    self.logger.warning(f"OpenAI ошибка: {result.get('message')}, переход на Ollama")

                if self.ollama and self.ollama.is_available:
                    self.current_provider = "ollama"
                    result = self.ollama.chat(message, context)
                    self.logger.info("LLM: сеть доступна, OpenAI ошибка, используется Ollama (фолбэк)")
                    return result

                return {
                    "status": "error",
                    "message": "Нет доступных LLM. OpenAI вернул ошибку, Ollama недоступен."
                }

            # ---- Нет интернета: приоритет Ollama ----
            else:
                self.logger.info("LLM: сеть недоступна, переключение на Ollama (локально)")

                if self.ollama and self.ollama.is_available:
                    self.current_provider = "ollama"
                    result = self.ollama.chat(message, context)
                    if result.get("status") == "ok":
                        return result
                    # Ollama не доступен — пробуем запустить и скачать модель
                    self.logger.warning(f"Ollama ошибка: {result.get('message')}, попытка авто-восстановления")

                    # Пытаемся запустить Ollama и загрузить модель
                    restore = self.ollama.ensure_ollama_running()
                    if restore["status"] == "ok":
                        pull = self.ollama.ensure_model_available(self.ollama.model)
                        if pull["status"] == "ok":
                            return self.ollama.chat(message, context)

                    return {
                        "status": "error",
                        "message": "Нет интернета и Ollama недоступен. Установите Ollama: https://ollama.com/download"
                    }

                # Ollama модуль не загружен вообще
                if self.ollama is None:
                    return {
                        "status": "error",
                        "message": "Нет интернета. Ollama модуль не загружен. Установите Ollama: https://ollama.com/download"
                    }

                return {
                    "status": "error",
                    "message": "Нет интернета и Ollama недоступен. Установите Ollama: https://ollama.com/download"
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
            "network_available": self._check_network(),
            "openai_available": self.openai is not None and self._check_openai_key(),
            "ollama_available": self.ollama is not None and self.ollama.is_available if self.ollama else False,
            "ollama_installed": self.ollama.ollama_installed if self.ollama else False
        }

    def list_providers(self) -> Dict:
        """Список доступных провайдеров."""
        providers = []

        if self.openai and self._check_openai_key():
            providers.append({
                "name": "openai",
                "status": "available",
                "model": self.openai.model,
                "requires_network": True
            })

        if self.ollama and self.ollama.is_available:
            providers.append({
                "name": "ollama",
                "status": "available",
                "model": self.ollama.model,
                "models": self.ollama.available_models,
                "requires_network": False
            })

        return {
            "status": "ok",
            "providers": providers,
            "current_mode": self.mode,
            "network_available": self._check_network()
        }


def create_llm_router(brain):
    """Фабричная функция для создания маршрутизатора."""
    return LLMRouter(brain)
