"""
App Launcher - Запуск приложений по голосовым командам JARVIS
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging


class AppLauncher:
    """Запуск приложений по голосовым командам."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.apps_file = Path("data/apps.json")
        self.apps_file.parent.mkdir(exist_ok=True)
        self.apps: Dict[str, str] = self._load_apps()

    def _load_apps(self) -> Dict[str, str]:
        """Загрузка списка приложений."""
        if self.apps_file.exists():
            with open(self.apps_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Стандартные приложения
        return {
            "блокнот": "notepad.exe",
            "калькулятор": "calc.exe",
            "проводник": "explorer.exe",
            "браузер": "chrome.exe",
            "хром": "chrome.exe",
            "яндекс": "firefox.exe",
            "edge": "msedge.exe",
            "терминал": "cmd.exe",
            "командная строка": "cmd.exe",
            "powershell": "powershell.exe",
            "настройки": "ms-settings:",
            "диспетчер задач": "taskmgr.exe",
            "paint": "mspaint.exe",
            "фотографии": "ms-photos:",
            "магазин": "ms-windows-store:",
            "почта": "outlookmail:",
            "календарь": "outlookcal:",
            "youtube": "https://youtube.com",
            "ютуб": "https://youtube.com",
            "гугл": "https://google.com",
            "github": "https://github.com",
            "телеграм": "telegram.exe",
            "discord": "discord.exe",
            "спотифай": "spotify.exe",
            "vlc": "vlc.exe",
        }

    def _save_apps(self):
        """Сохранение списка приложений."""
        with open(self.apps_file, 'w', encoding='utf-8') as f:
            json.dump(self.apps, f, ensure_ascii=False, indent=2)

    def launch(self, app_name: str) -> Dict:
        """Запуск приложения."""
        app_name_lower = app_name.lower().strip()

        # Поиск в списке
        if app_name_lower in self.apps:
            app_path = self.apps[app_name_lower]

            try:
                # Если это URL
                if app_path.startswith("http://") or app_path.startswith("https://"):
                    subprocess.Popen(["start", app_path], shell=True)
                    return {"status": "ok", "message": f"Открываю {app_name}..."}

                # Если это команда Windows
                elif app_path.startswith("ms-"):
                    subprocess.Popen(["start", app_path], shell=True)
                    return {"status": "ok", "message": f"Открываю {app_name}..."}

                # Если это exe файл
                else:
                    subprocess.Popen(app_path, shell=True)
                    return {"status": "ok", "message": f"Запускаю {app_name}..."}

            except Exception as e:
                self.logger.error(f"Ошибка запуска {app_name}: {e}")
                return {"status": "error", "message": f"Не удалось запустить {app_name}: {e}"}

        return {"status": "error", "message": f"Приложение '{app_name}' не найдено. Скажите 'добавь приложение {app_name}'"}

    def add_app(self, name: str, path: str) -> Dict:
        """Добавить новое приложение."""
        name_lower = name.lower().strip()
        self.apps[name_lower] = path
        self._save_apps()

        self.logger.info(f"Добавлено приложение: {name} → {path}")
        return {"status": "ok", "message": f"Приложение '{name}' добавлено"}

    def remove_app(self, name: str) -> Dict:
        """Удалить приложение."""
        name_lower = name.lower().strip()

        if name_lower in self.apps:
            del self.apps[name_lower]
            self._save_apps()
            return {"status": "ok", "message": f"Приложение '{name}' удалено"}

        return {"status": "error", "message": f"Приложение '{name}' не найдено"}

    def list_apps(self) -> Dict:
        """Список всех приложений."""
        apps_list = [f"• {name}" for name in sorted(self.apps.keys())]
        return {
            "status": "ok",
            "message": f"Всего {len(self.apps)} приложений:\n" + "\n".join(apps_list[:20]) + ("\n..." if len(apps_list) > 20 else "")
        }

    def get_apps_count(self) -> int:
        """Количество приложений."""
        return len(self.apps)
