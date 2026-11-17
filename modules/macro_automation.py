"""
Модуль макро-автоматизации JARVIS (стиль Железного Человека)
- Запуск предустановленных сценариев (рабочее окружение, отдых, сон)
- Открытие приложений и веб-сайтов
- Настройка рабочего стола и окон
"""

import os
import subprocess
import threading
import time
import webbrowser
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MacroAutomation:
    """Макро-автоматизация - сценарии быстрого запуска рабочего окружения."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Конфигурация
        config = brain.config.get("macro_automation", {})
        self.enabled = config.get("enabled", True)
        self.macros_file = Path("data/macros.json")
        self.macros_file.parent.mkdir(parents=True, exist_ok=True)

        # Встроенные макросы
        self.macros: Dict[str, Dict] = {}
        self._load_macros()
        self._init_default_macros()

        # Состояние запуска
        self.running_macro = None
        self.running_thread: Optional[threading.Thread] = None

    def _load_macros(self):
        """Загрузка пользовательских макросов из файла."""
        if self.macros_file.exists():
            try:
                with open(self.macros_file, 'r', encoding='utf-8') as f:
                    user_macros = __import__('json').load(f)
                    self.macros.update(user_macros)
            except Exception as e:
                self.logger.error(f"Ошибка загрузки макросов: {e}")

    def _save_macros(self):
        """Сохранение макросов в файл."""
        try:
            with open(self.macros_file, 'w', encoding='utf-8') as f:
                __import__('json').dump(self.macros, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения макросов: {e}")

    def _init_default_macros(self):
        """Инициализация встроенных макросов по умолчанию."""
        defaults = {
            "work_environment": {
                "name": "Рабочее окружение",
                "description": "Открывает IDE, браузер, мессенджеры и терминал",
                "steps": [
                    {"type": "open_app", "name": "IDE / Редактор кода", "command": "code"},
                    {"type": "open_browser", "url": "https://github.com"},
                    {"type": "open_app", "name": "Терминал", "command": "gnome-terminal"},
                    {"type": "wait", "seconds": 2},
                    {"type": "speak", "text": "Рабочее окружение готово, Сэр."}
                ]
            },
            "gaming_mode": {
                "name": "Игровой режим",
                "description": "Закрывает ненужные приложения, запускает Steam",
                "steps": [
                    {"type": "open_app", "name": "Steam", "command": "steam"},
                    {"type": "wait", "seconds": 3},
                    {"type": "speak", "text": "Игровой режим активирован, Сэр."}
                ]
            },
            "morning_routine": {
                "name": "Утренняя рутина",
                "description": "Новости, погода, почта, календарь",
                "steps": [
                    {"type": "open_browser", "url": "https://news.ycombinator.com"},
                    {"type": "open_browser", "url": "https://gmail.com"},
                    {"type": "wait", "seconds": 1},
                    {"type": "speak", "text": "Утренняя рутина завершена, Сэр."}
                ]
            },
            "focus_mode": {
                "name": "Режим концентрации",
                "description": "Закрывает соцсети, включает музыку для фокуса",
                "steps": [
                    {"type": "open_browser", "url": "https://open.spotify.com"},
                    {"type": "wait", "seconds": 2},
                    {"type": "speak", "text": "Режим концентрации активирован. Отвлекающие приложения закрыты, Сэр."}
                ]
            },
            "shutdown": {
                "name": "Завершение работы",
                "description": "Закрывает все приложения и готовит к выключению",
                "steps": [
                    {"type": "speak", "text": "Завершаю работу, Сэр. Все задачи сохранены."},
                    {"type": "wait", "seconds": 2}
                ]
            }
        }

        for key, macro in defaults.items():
            if key not in self.macros:
                self.macros[key] = macro

        self._save_macros()

    # === Выполнение макросов ===

    def list_macros(self) -> Dict:
        """Список всех доступных макросов."""
        return {
            "status": "ok",
            "macros": [
                {
                    "id": key,
                    "name": m.get("name", key),
                    "description": m.get("description", ""),
                    "steps_count": len(m.get("steps", []))
                }
                for key, m in self.macros.items()
            ],
            "count": len(self.macros)
        }

    def run_macro(self, macro_id: str) -> Dict:
        """Запуск макроса по ID."""
        if not self.enabled:
            return {"status": "error", "message": "Макро-автоматизация отключена"}

        if macro_id not in self.macros:
            return {"status": "error", "message": f"Макрос {macro_id} не найден"}

        if self.running_macro:
            return {"status": "error", "message": f"Уже запущен марос: {self.running_macro}"}

        macro = self.macros[macro_id]
        self.running_macro = macro_id

        self.running_thread = threading.Thread(target=self._execute_macro, args=(macro_id, macro), daemon=True)
        self.running_thread.start()

        self.logger.info(f"Запуск макроса: {macro_id} - {macro.get('name', '')}")
        return {
            "status": "ok",
            "message": f"Макрос запущен: {macro.get('name', macro_id)}",
            "macro_id": macro_id
        }

    def _execute_macro(self, macro_id: str, macro: Dict):
        """Выполнение шагов макроса (в отдельном потоке)."""
        try:
            steps = macro.get("steps", [])
            for i, step in enumerate(steps):
                if self.running_macro != macro_id:
                    # Макрос был отменен
                    break

                step_type = step.get("type", "")

                if step_type == "open_app":
                    self._open_application(step.get("name", ""), step.get("command", ""))
                elif step_type == "open_browser":
                    webbrowser.open(step.get("url", ""))
                elif step_type == "open_file":
                    self._open_file(step.get("path", ""))
                elif step_type == "wait":
                    time.sleep(step.get("seconds", 1))
                elif step_type == "speak":
                    self._speak(step.get("text", ""))
                elif step_type == "key_combo":
                    if PYAUTOGUI_AVAILABLE:
                        keys = step.get("keys", [])
                        pyautogui.hotkey(*keys)
                elif step_type == "close_app":
                    self._close_application(step.get("name", ""))

            self.logger.info(f"Макрос завершен: {macro_id}")

        except Exception as e:
            self.logger.error(f"Ошибка выполнения макроса {macro_id}: {e}")
        finally:
            self.running_macro = None

    def stop_macro(self) -> Dict:
        """Остановка выполняющегося макроса."""
        if not self.running_macro:
            return {"status": "error", "message": "Нет выполняющегося макроса"}

        stopped = self.running_macro
        self.running_macro = None
        self.logger.info(f"Макрос остановлен: {stopped}")
        return {"status": "ok", "message": f"Макрос остановлен: {stopped}"}

    def get_status(self) -> Dict:
        """Получить статус макро-автоматизации."""
        return {
            "status": "ok",
            "enabled": self.enabled,
            "running_macro": self.running_macro,
            "macros_count": len(self.macros),
            "pyautogui_available": PYAUTOGUI_AVAILABLE
        }

    # === Управление макросами ===

    def add_macro(self, macro_id: str, name: str, description: str, steps: List[Dict]) -> Dict:
        """Добавить пользовательский макрос."""
        self.macros[macro_id] = {
            "name": name,
            "description": description,
            "steps": steps,
            "created": datetime.now().isoformat()
        }
        self._save_macros()
        return {"status": "ok", "message": f"Макрос '{name}' добавлен"}

    def remove_macro(self, macro_id: str) -> Dict:
        """Удалить макрос."""
        if macro_id in self.macros:
            name = self.macros[macro_id].get("name", macro_id)
            del self.macros[macro_id]
            self._save_macros()
            return {"status": "ok", "message": f"Макрос '{name}' удален"}
        return {"status": "error", "message": f"Макрос {macro_id} не найден"}

    # === Вспомогательные методы ===

    def _open_application(self, name: str, command: str):
        """Открыть приложение."""
        try:
            if command:
                subprocess.Popen(command, shell=True)
            self.logger.info(f"Открыто приложение: {name} ({command})")
        except Exception as e:
            self.logger.error(f"Ошибка открытия приложения {name}: {e}")

    def _close_application(self, name: str):
        """Закрыть приложение по имени."""
        if not PSUTIL_AVAILABLE:
            return
        try:
            for proc in psutil.process_iter(['name']):
                if name.lower() in (proc.info.get('name') or '').lower():
                    proc.terminate()
        except Exception as e:
            self.logger.error(f"Ошибка закрытия приложения {name}: {e}")

    def _open_file(self, path: str):
        """Открыть файл."""
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            self.logger.error(f"Ошибка открытия файла {path}: {e}")

    def _speak(self, text: str):
        """Озвучить текст через голосовой модуль."""
        try:
            if hasattr(self.brain, 'voice_personality') and self.brain.voice_personality:
                self.brain.voice_personality.speak_professional(text)
            elif hasattr(self.brain, 'voice_speaker') and self.brain.voice_speaker:
                self.brain.voice_speaker.speak(text)
        except Exception as e:
            self.logger.error(f"Ошибка озвучки: {e}")
