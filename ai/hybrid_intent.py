"""
JARVIS Hybrid Intent System
Быстрые локальные правила + AI fallback
"""

import re
from typing import Optional, Dict, Any, Callable
from datetime import datetime

class HybridIntentSystem:
    """Гибридная система обработки команд"""

    def __init__(self, ai_fallback=None):
        self.rules: Dict[str, Dict] = {}
        self.ai_fallback = ai_fallback
        self._init_default_rules()

    def _init_default_rules(self):
        """Инициализация правил по умолчанию"""

        self.add_rule(
            name="time_query",
            patterns=[r"который час", r"сколько времени", r"what time"],
            handler=self._handle_time,
            priority=10
        )

        self.add_rule(
            name="date_query",
            patterns=[r"какая сегодня дата", r"какой день", r"what date"],
            handler=self._handle_date,
            priority=10
        )

        self.add_rule(
            name="volume_up",
            patterns=[r"громче", r"увеличь громкость", r"volume up"],
            handler=self._handle_volume_up,
            priority=8
        )

        self.add_rule(
            name="volume_down",
            patterns=[r"тише", r"уменьши громкость", r"volume down"],
            handler=self._handle_volume_down,
            priority=8
        )

        self.add_rule(
            name="open_app",
            patterns=[r"открой (.+)", r"запусти (.+)", r"open (.+)"],
            handler=self._handle_open_app,
            priority=5
        )

        self.add_rule(
            name="web_search",
            patterns=[r"найди в интернете (.+)", r"погугли (.+)", r"search (.+)"],
            handler=self._handle_web_search,
            priority=6
        )

    def add_rule(self, name: str, patterns: list, handler: Callable, priority: int = 5):
        """Добавление нового правила"""
        self.rules[name] = {
            'patterns': [re.compile(p, re.IGNORECASE) for p in patterns],
            'handler': handler,
            'priority': priority
        }

    def process_command(self, command: str) -> Dict[str, Any]:
        """Обработка команды"""
        command_lower = command.lower().strip()

        sorted_rules = sorted(
            self.rules.items(),
            key=lambda x: x[1]['priority'],
            reverse=True
        )

        for rule_name, rule_data in sorted_rules:
            for pattern in rule_data['patterns']:
                match = pattern.search(command_lower)
                if match:
                    try:
                        args = match.groups() if match.groups() else ()
                        result = rule_data['handler'](command, *args)

                        return {
                            'success': True,
                            'method': 'local_rule',
                            'rule': rule_name,
                            'result': result
                        }
                    except Exception as e:
                        return {
                            'success': False,
                            'method': 'local_rule',
                            'rule': rule_name,
                            'error': str(e)
                        }

        if self.ai_fallback:
            try:
                ai_result = self.ai_fallback(command)
                return {
                    'success': True,
                    'method': 'ai_fallback',
                    'result': ai_result
                }
            except Exception as e:
                return {
                    'success': False,
                    'method': 'ai_fallback',
                    'error': str(e)
                }

        return {
            'success': False,
            'method': 'none',
            'error': 'Команда не распознана'
        }

    def _handle_time(self, command: str) -> str:
        now = datetime.now()
        return f"Сейчас {now.strftime('%H:%M')}"

    def _handle_date(self, command: str) -> str:
        now = datetime.now()
        return f"Сегодня {now.strftime('%d.%m.%Y')}, {now.strftime('%A')}"

    def _handle_volume_up(self, command: str) -> str:
        import subprocess
        subprocess.run(["powershell", "-command", "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"])
        return "Громкость увеличена"

    def _handle_volume_down(self, command: str) -> str:
        import subprocess
        subprocess.run(["powershell", "-command", "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"])
        return "Громкость уменьшена"

    def _handle_open_app(self, command: str, app_name: str = None) -> str:
        if not app_name:
            return "Какое приложение открыть?"

        import subprocess
        try:
            subprocess.Popen(app_name, shell=True)
            return f"Приложение {app_name} запущено"
        except Exception as e:
            return f"Не удалось запустить {app_name}: {e}"

    def _handle_web_search(self, command: str, query: str = None) -> str:
        if not query:
            return "Что найти?"

        import webbrowser
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Открыт поиск: {query}"
