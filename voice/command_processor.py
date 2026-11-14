"""
Обработчик голосовых команд для JARVIS
Интеграция с ML-движком для понимания новых команд
"""

import re
import json
from typing import Dict, List, Optional, Callable, Tuple
from pathlib import Path


class CommandProcessor:
    """Обработка голосовых команд с ML-классификацией."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.config = brain.config

        # ML-движок (если доступен)
        self.ml_engine = getattr(brain, 'ml_engine', None)

        # Словарь команд
        self.commands: Dict[str, Dict] = {}
        self.patterns: Dict[str, List[str]] = {}

        # Callbacks
        self.on_command_executed: Optional[Callable[[str, Dict], None]] = None
        self.on_unknown_command: Optional[Callable[[str], None]] = None

        # Загрузка команд
        self._load_commands()
        self._init_patterns()

    def _load_commands(self):
        """Загрузка команд из конфигурации."""
        # Базовые команды
        self.commands = {
            # Системные команды
            "shutdown": {
                "action": "system.shutdown",
                "description": "Выключение компьютера",
                "confirm": True
            },
            "restart": {
                "action": "system.restart",
                "description": "Перезагрузка компьютера",
                "confirm": True
            },
            "lock": {
                "action": "system.lock_screen",
                "description": "Блокировка экрана",
                "confirm": False
            },
            "sleep": {
                "action": "system.sleep",
                "description": "Спящий режим",
                "confirm": False
            },
            "cancel_shutdown": {
                "action": "system.cancel_shutdown",
                "description": "Отмена выключения",
                "confirm": False
            },

            # Управление рабочим столом
            "minimize_all": {
                "action": "desktop.minimize_all",
                "description": "Свернуть все окна",
                "confirm": False
            },
            "show_desktop": {
                "action": "desktop.show_desktop",
                "description": "Показать рабочий стол",
                "confirm": False
            },
            "volume_up": {
                "action": "desktop.volume_up",
                "description": "Увеличить громкость",
                "confirm": False
            },
            "volume_down": {
                "action": "desktop.volume_down",
                "description": "Уменьшить громкость",
                "confirm": False
            },
            "mute": {
                "action": "desktop.mute",
                "description": "Выключить звук",
                "confirm": False
            },

            # Управление голосом
            "start_listening": {
                "action": "voice.start_listening",
                "description": "Начать слушать",
                "confirm": False
            },
            "stop_listening": {
                "action": "voice.stop_listening",
                "description": "Перестать слушать",
                "confirm": False
            },

            # Информация
            "time": {
                "action": "info.get_time",
                "description": "Текущее время",
                "confirm": False
            },
            "date": {
                "action": "info.get_date",
                "description": "Текущая дата",
                "confirm": False
            },
            "weather": {
                "action": "info.get_weather",
                "description": "Погода",
                "confirm": False
            },

            # Приложения
            "open_notepad": {
                "action": "app.open_notepad",
                "description": "Открыть блокнот",
                "confirm": False
            },
            "open_calculator": {
                "action": "app.open_calculator",
                "description": "Открыть калькулятор",
                "confirm": False
            },
            "open_browser": {
                "action": "app.open_browser",
                "description": "Открыть браузер",
                "confirm": False
            },
        }

    def _init_patterns(self):
        """Инициализация паттернов для распознавания команд."""
        self.patterns = {
            "shutdown": [
                r"выключи(?:те)?(?:\s+компьютер)?",
                r"заверши(?:те)?\s+работу",
                r"выключить\s+пк",
                r"shutdown",
            ],
            "restart": [
                r"перезагрузи(?:те)?(?:\s+компьютер)?",
                r"перезагрузи(?:те)?\s+пк",
                r"рестарт",
                r"restart",
            ],
            "lock": [
                r"заблокируй(?:те)?(?:\s+экран)?",
                r"заблокируй(?:те)?\s+компьютер",
                r"лок",
                r"lock",
            ],
            "sleep": [
                r"спящий\s+режим",
                r"усни(?:те)?",
                r"сон",
                r"sleep",
            ],
            "cancel_shutdown": [
                r"отмени(?:те)?\s+выключение",
                r"не\s+выключай",
                r"отмена\s+выключения",
            ],
            "minimize_all": [
                r"сверни(?:те)?\s+все\s+окна",
                r"сверни(?:те)?\s+все",
                r"покажи(?:те)?\s+рабочий\s+стол",
                r"рабочий\s+стол",
            ],
            "show_desktop": [
                r"покажи(?:те)?\s+рабочий\s+стол",
                r"на\s+рабочий\s+стол",
            ],
            "volume_up": [
                r"громче",
                r"увеличь(?:те)?\s+громкость",
                r"сделай(?:те)?\s+громче",
                r"добавь(?:те)?\s+звука",
            ],
            "volume_down": [
                r"тише",
                r"уменьши(?:те)?\s+громкость",
                r"сделай(?:те)?\s+тише",
                r"убавь(?:те)?\s+звука",
            ],
            "mute": [
                r"без\s+звука",
                r"выключи(?:те)?\s+звук",
                r"mute",
                r"мьют",
            ],
            "start_listening": [
                r"начни(?:те)?\s+слушать",
                r"включи(?:те)?\s+микрофон",
                r"слушай",
            ],
            "stop_listening": [
                r"перестань(?:те)?\s+слушать",
                r"выключи(?:те)?\s+микрофон",
                r"стоп",
                r"хватит",
            ],
            "time": [
                r"который\s+час",
                r"сколько\s+времени",
                r"время",
                r"текущее\s+время",
            ],
            "date": [
                r"какая\s+дата",
                r"какое\s+сегодня\s+число",
                r"дата",
                r"сегодняшний\s+день",
            ],
            "weather": [
                r"какая\s+погода",
                r"погода\s+на\s+сегодня",
                r"прогноз\s+погоды",
                r"погода",
            ],
            "open_notepad": [
                r"открой(?:те)?\s+блокнот",
                r"запусти(?:те)?\s+блокнот",
                r"notepad",
            ],
            "open_calculator": [
                r"открой(?:те)?\s+калькулятор",
                r"запусти(?:те)?\s+калькулятор",
                r"calculator",
            ],
            "open_browser": [
                r"открой(?:те)?\s+браузер",
                r"запусти(?:те)?\s+браузер",
                r"интернет",
            ],
        }

    def process(self, text: str) -> Dict:
        """Обработка текстовой команды."""
        if not text or not text.strip():
            return {"status": "error", "message": "Пустая команда"}

        text = text.strip().lower()
        self.logger.info(f"Обработка команды: {text}")

        # 1. Попытка найти по паттернам
        command = self._match_pattern(text)
        if command:
            return self._execute_command(command, text)

        # 2. Попытка ML-классификации
        if self.ml_engine:
            ml_result = self._ml_classify(text)
            if ml_result and ml_result.get("confidence", 0) > 0.7:
                command = ml_result.get("category")
                if command in self.commands:
                    return self._execute_command(command, text)

        # 3. Команда не распознана
        if self.on_unknown_command:
            self.on_unknown_command(text)

        return {
            "status": "unknown",
            "message": f"Команда не распознана: {text}",
            "suggestion": "Попробуйте переформулировать или обучить меня новой команде"
        }

    def _match_pattern(self, text: str) -> Optional[str]:
        """Поиск команды по паттернам."""
        for command, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return command
        return None

    def _ml_classify(self, text: str) -> Optional[Dict]:
        """ML-классификация команды."""
        try:
            if hasattr(self.ml_engine, 'predict'):
                return self.ml_engine.predict(text)
        except Exception as e:
            self.logger.debug(f"ML классификация не удалась: {e}")
        return None

    def _execute_command(self, command: str, original_text: str) -> Dict:
        """Выполнение команды."""
        cmd_config = self.commands.get(command)
        if not cmd_config:
            return {"status": "error", "message": f"Команда {command} не найдена"}

        action = cmd_config.get("action")
        if not action:
            return {"status": "error", "message": "Действие не указано"}

        # Выполнение действия через brain
        try:
            result = self.brain.execute_action(action)

            if self.on_command_executed:
                self.on_command_executed(command, result)

            return {
                "status": "ok",
                "command": command,
                "action": action,
                "result": result
            }
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды {command}: {e}")
            return {"status": "error", "message": str(e)}

    def add_command(self, name: str, config: Dict) -> Dict:
        """Добавление новой команды."""
        if name in self.commands:
            return {"status": "error", "message": f"Команда {name} уже существует"}

        self.commands[name] = config
        self.logger.info(f"Добавлена команда: {name}")
        return {"status": "ok", "message": f"Команда {name} добавлена"}

    def add_pattern(self, command: str, patterns: List[str]) -> Dict:
        """Добавление паттернов для команды."""
        if command not in self.patterns:
            self.patterns[command] = []

        self.patterns[command].extend(patterns)
        self.logger.info(f"Добавлено {len(patterns)} паттернов для команды {command}")
        return {"status": "ok", "message": f"Паттерны добавлены для {command}"}

    def get_commands(self) -> Dict:
        """Получить список всех команд."""
        return {
            "status": "ok",
            "commands": {
                name: {
                    "description": cmd.get("description"),
                    "confirm": cmd.get("confirm", False)
                }
                for name, cmd in self.commands.items()
            }
        }

    def get_patterns(self) -> Dict:
        """Получить все паттерны."""
        return {
            "status": "ok",
            "patterns": self.patterns
        }

    def learn_from_example(self, text: str, command: str) -> Dict:
        """Обучение на примере (интеграция с ML)."""
        if self.ml_engine and hasattr(self.ml_engine, 'add_training_example'):
            result = self.ml_engine.add_training_example(text, command)
            if result.get("status") == "ok":
                # Добавляем паттерн для будущего распознавания
                self.add_pattern(command, [re.escape(text)])
                return result
        return {"status": "error", "message": "ML-движок не доступен"}

    def save_commands(self, file_path: str = "data/commands.json") -> Dict:
        """Сохранение команд в файл."""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            data = {
                "commands": self.commands,
                "patterns": self.patterns
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return {"status": "ok", "message": f"Команды сохранены в {file_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def load_commands_from_file(self, file_path: str = "data/commands.json") -> Dict:
        """Загрузка команд из файла."""
        try:
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.commands.update(data.get("commands", {}))
                self.patterns.update(data.get("patterns", {}))
                return {"status": "ok", "message": f"Команды загружены из {file_path}"}
            return {"status": "error", "message": f"Файл не найден: {file_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
