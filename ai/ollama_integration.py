"""
JARVIS Ollama Integration
Local LLM support with automatic fallback and auto-download
"""

import os
import sys
import json
import subprocess
import platform
import shutil
import requests
from typing import Dict, List, Optional
from datetime import datetime


class OllamaIntegration:
    """Интеграция с локальной LLM через Ollama с авто-загрузкой."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Настройки из конфига
        ai_config = brain.config.get("ai", {})
        ollama_config = ai_config.get("ollama", {})
        self.base_url = ollama_config.get("base_url", "http://localhost:11434")
        self.model = ollama_config.get("default_model", "llama3.2")
        self.auto_download = ollama_config.get("auto_download", True)
        self.available_models: List[str] = []

        # Контекст разговора
        self.conversation_history: List[Dict] = []
        self.max_history = 20

        # Статус
        self.is_available = False
        self.ollama_installed = False

        # Инициализация
        self._detect_ollama_install()
        self._check_ollama()

    # === ОБНАРУЖЕНИЕ И УСТАНОВКА OLLAMA ===

    def _detect_ollama_install(self) -> bool:
        """Проверка, установлен ли Ollama на системе."""
        self.ollama_installed = shutil.which("ollama") is not None
        if self.ollama_installed:
            self.logger.info("Ollama CLI найден в системе")
        else:
            self.logger.warning("Ollama CLI не найден. Будет предложена установка.")
        return self.ollama_installed

    def is_ollama_installed(self) -> bool:
        """Проверить, установлен ли Ollama."""
        return self.ollama_installed

    def install_ollama(self) -> Dict:
        """Авто-установка Ollama (Windows/Linux/Mac)."""
        system = platform.system().lower()
        self.logger.info(f"Начало установки Ollama для {system}...")

        try:
            if system == "windows":
                # Windows: скачать и запустить установщик
                url = "https://ollama.com/download/OllamaSetup.exe"
                installer_path = os.path.join(os.getcwd(), "OllamaSetup.exe")
                self.logger.info(f"Скачивание Ollama установщика: {url}")
                try:
                    import urllib.request
                    urllib.request.urlretrieve(url, installer_path)
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Не удалось скачать Ollama: {e}. "
                                   f"Установите вручную с https://ollama.com/download"
                    }
                return {
                    "status": "ok",
                    "message": f"Ollama установщик скачан: {installer_path}. "
                               f"Запустите установщик вручную.",
                    "installer_path": installer_path
                }

            elif system == "linux":
                # Linux: curl | sh скрипт установки
                install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
                self.logger.info(f"Выполнение: {install_cmd}")
                result = subprocess.run(
                    install_cmd, shell=True, capture_output=True, text=True, timeout=120
                )
                if result.returncode == 0:
                    self.ollama_installed = True
                    self.logger.info("Ollama установлен успешно")
                    return {"status": "ok", "message": "Ollama установлен успешно"}
                else:
                    return {
                        "status": "error",
                        "message": f"Ошибка установки Ollama: {result.stderr}"
                    }

            elif system == "darwin":
                # macOS
                url = "https://ollama.com/download/Ollama-darwin.zip"
                return {
                    "status": "ok",
                    "message": f"Скачайте Ollama вручную: {url}"
                }

            else:
                return {
                    "status": "error",
                    "message": f"Неподдерживаемая ОС: {system}"
                }

        except Exception as e:
            self.logger.error(f"Ошибка установки Ollama: {e}")
            return {"status": "error", "message": str(e)}

    def ensure_ollama_running(self) -> Dict:
        """Убедиться, что Ollama сервер запущен. Если нет — попытка запустить."""
        if self._check_ollama():
            return {"status": "ok", "message": "Ollama уже запущен"}

        if not self.ollama_installed:
            return self.install_ollama()

        # Ollama установлен, но сервер не запущен — попробуем запустить
        try:
            system = platform.system().lower()
            if system == "windows":
                subprocess.Popen(["ollama", "serve"], shell=True,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["ollama", "serve"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Подождать, пока сервер запустится
            import time
            for _ in range(15):
                time.sleep(1)
                if self._check_ollama():
                    return {"status": "ok", "message": "Ollama сервер запущен"}

            return {
                "status": "error",
                "message": "Ollama сервер не запустился за отведённое время"
            }
        except Exception as e:
            self.logger.error(f"Ошибка запуска Ollama сервера: {e}")
            return {"status": "error", "message": str(e)}

    # === АВТО-ЗАГРУЗКА МОДЕЛЕЙ ===

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

    def pull_model(self, model_name: str) -> Dict:
        """Авто-загрузка модели Ollama через API."""
        if not self.is_available:
            result = self.ensure_ollama_running()
            if result["status"] != "ok":
                return result

        if model_name in self.available_models:
            return {
                "status": "ok",
                "message": f"Модель {model_name} уже доступна",
                "model": model_name
            }

        self.logger.info(f"Начало загрузки модели Ollama: {model_name}")
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300,
                stream=True
            )

            if response.status_code == 200:
                # Читаем потоковый ответ для отслеживания прогресса
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            status = data.get("status", "")
                            if "success" in status.lower() or status == "success":
                                self.available_models.append(model_name)
                                self.logger.info(f"Модель {model_name} загружена успешно")
                                return {
                                    "status": "ok",
                                    "message": f"Модель {model_name} загружена успешно",
                                    "model": model_name
                                }
                        except json.JSONDecodeError:
                            continue

                return {
                    "status": "ok",
                    "message": f"Модель {model_name} загружена",
                    "model": model_name
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка загрузки модели: HTTP {response.status_code}"
                }

        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": f"Таймаут загрузки модели {model_name}. Попробуйте позже."
            }
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модели {model_name}: {e}")
            return {"status": "error", "message": str(e)}

    def ensure_model_available(self, model_name: Optional[str] = None) -> Dict:
        """Убедиться, что модель доступна. Если нет — авто-загрузка."""
        target = model_name or self.model

        if target in self.available_models:
            return {"status": "ok", "message": f"Модель {target} уже доступна", "model": target}

        if not self.auto_download:
            return {
                "status": "error",
                "message": f"Модель {target} недоступна. Авто-загрузка отключена."
            }

        self.logger.info(f"Модель {target} не найдена, начинаю авто-загрузку...")
        return self.pull_model(target)

    def set_model(self, model: str) -> Dict:
        """Установить модель Ollama с авто-загрузкой при необходимости."""
        if not self.is_available:
            result = self.ensure_ollama_running()
            if result["status"] != "ok":
                return result

        # Сначала пытаемся загрузить модель, если её нет
        if model not in self.available_models:
            pull_result = self.pull_model(model)
            if pull_result["status"] != "ok":
                return pull_result

        self.model = model
        self.logger.info(f"Модель Ollama изменена на {model}")
        return {"status": "ok", "message": f"Модель изменена на {model}"}

    def list_models(self) -> Dict:
        """Список доступных моделей."""
        if not self.is_available:
            if self.ensure_ollama_running()["status"] != "ok":
                return {"status": "error", "message": "Ollama недоступен"}

        return {
            "status": "ok",
            "models": self.available_models,
            "current": self.model,
            "auto_download": self.auto_download
        }

    # === ЧАТ ===

    def chat(self, message: str, context: str = "") -> Dict:
        """Отправить сообщение в локальную LLM."""
        # Убедиться, что Ollama запущен и модель доступна
        if not self.is_available:
            result = self.ensure_ollama_running()
            if result["status"] != "ok":
                return result

        # Убедиться, что модель загружена
        model_result = self.ensure_model_available(self.model)
        if model_result["status"] != "ok":
            return model_result

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
                timeout=120
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
            "ollama_installed": self.ollama_installed,
            "model": self.model,
            "available_models": self.available_models,
            "auto_download": self.auto_download,
            "history_count": len(self.conversation_history)
        }


def create_ollama_module(brain):
    """Фабричная функция для создания модуля Ollama."""
    return OllamaIntegration(brain)
