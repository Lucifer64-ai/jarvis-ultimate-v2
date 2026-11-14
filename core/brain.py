"""JARVIS Brain - Главный контроллер и обработка команд"""

import logging
from typing import Dict

from core.config import Config
from core.event_bus import EventBus
from core.plugin_manager import PluginManager
from agents.agent_manager import AgentManager
from agents.file_saver import get_file_saver


class JarvisBrain:
    """Главный контроллер и обработка команд JARVIS."""

    def __init__(self):
        self.logger = self._setup_logging()
        self.logger.info("Инициализация JARVIS Brain...")
        self.config = Config()
        self.event_bus = EventBus()
        self.plugin_manager = PluginManager(self)
        self.agent_manager = AgentManager()
        self.file_saver = get_file_saver()
        self.learning_manager = None
        self.windows_integration = None
        self.toast_notifications = None
        self.wake_word_service = None
        self.clean_desktop = None
        self.app_launcher = None
        self.hud = None
        self.weather_module = None
        self.currency_module = None
        self.news_module = None
        self.modules = {}
        self.running = False
        self.logger.info("JARVIS Brain инициализирован")
        self._init_modules()
        self._init_voice()

    def _setup_logging(self):
        logger = logging.getLogger("JARVIS")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        logger.addHandler(handler)
        return logger

    def _init_modules(self):
        """Инициализация всех модулей системы."""
        # Windows интеграция
        try:
            from modules.windows_integration import WindowsIntegration
            self.windows_integration = WindowsIntegration(self)
            self.logger.info("Модуль Windows интеграции загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки Windows интеграции: {e}")
            self.windows_integration = None

        # Toast уведомления
        try:
            from modules.toast_notifications import ToastNotifications
            self.toast_notifications = ToastNotifications(self)
            self.logger.info("Модуль уведомлений загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля уведомлений: {e}")
            self.toast_notifications = None

        # Wake word сервис
        try:
            from modules.wake_word_service import WakeWordService
            self.wake_word_service = WakeWordService(self)
            self.logger.info("Модуль Wake word загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля wake word: {e}")
            self.wake_word_service = None

        # Clean Desktop
        try:
            from modules.clean_desktop import CleanDesktop
            self.clean_desktop = CleanDesktop(self)
            self.logger.info("Модуль Clean Desktop загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Clean Desktop: {e}")
            self.clean_desktop = None

        # App Launcher
        try:
            from modules.app_launcher import AppLauncher
            self.app_launcher = AppLauncher(self)
            self.logger.info("Модуль App Launcher загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля App Launcher: {e}")
            self.app_launcher = None

    def _init_voice(self):
        """Инициализация голосовых модулей."""
        try:
            from voice.speaker import VoiceSpeaker
            self.voice_speaker = VoiceSpeaker(self)
            self.logger.info("Модуль синтеза речи загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля синтеза речи: {e}")
            self.voice_speaker = None

    def _handle_agent_voice_command(self, text: str) -> Dict:
        """Обработка голосовых команд для управления агентами."""
        text_lower = text.lower()

        # Команда: список агентов
        if any(phrase in text_lower for phrase in ["какие агенты", "список агентов", "покажи агентов"]):
            agents = self.agent_manager.list_agents()
            agent_list = "\n".join([f"• {a['name']}: {a['description']}" for a in agents])
            return {
                "status": "success",
                "message": f"Активные агенты:\n{agent_list}",
                "type": "agent_list"
            }

        # Команда: история задач
        elif any(phrase in text_lower for phrase in ["история задач", "что делали агенты", "последние задачи"]):
            history = self.agent_manager.get_task_history()[:10]
            if not history:
                return {
                    "status": "success",
                    "message": "История задач пуста",
                    "type": "task_history"
                }

            task_list = "\n".join([
                f"• {h['timestamp'][:16]} - {h['agent']}: {h['task'][:50]}"
                for h in history
            ])
            return {
                "status": "success",
                "message": f"Последние задачи:\n{task_list}",
                "type": "task_history"
            }

        # Команда: возможности агента
        elif any(phrase in text_lower for phrase in ["возможности агента", "что может агент"]):
            for agent_name in ["Web Developer", "Programmer", "Data Analyst", "Designer", "DevOps"]:
                if agent_name.lower() in text_lower:
                    agent = self.agent_manager.get_agent(agent_name)
                    if agent:
                        capabilities = "\n".join([f"• {cap}" for cap in agent.capabilities])
                        return {
                            "status": "success",
                            "message": f"Возможности {agent_name}:\n{capabilities}",
                            "type": "agent_capabilities"
                        }

            return {
                "status": "error",
                "message": "Укажите имя агента: Web Developer, Programmer, Data Analyst, Designer или DevOps"
            }

        # Команда: статус агента
        elif any(phrase in text_lower for phrase in ["статус агента", "состояние агента"]):
            for agent_name in ["Web Developer", "Programmer", "Data Analyst", "Designer", "DevOps"]:
                if agent_name.lower() in text_lower:
                    agent = self.agent_manager.get_agent(agent_name)
                    if agent:
                        status = agent.get_status()
                        return {
                            "status": "success",
                            "message": f"Статус {agent_name}:\n• Активен: {status['is_active']}\n• Задач выполнено: {status['tasks_completed']}",
                            "type": "agent_status"
                        }

            return {
                "status": "error",
                "message": "Укажите имя агента"
            }

        return {
            "status": "error",
            "message": "Неизвестная команда управления агентами"
        }

    def _handle_agent_task(self, text: str) -> Dict:
        """Делегирование задачи через систему агентов."""
        self.logger.info(f"Передача задачи агенту: {text}")

        try:
            result = self.agent_manager.execute_task(text)

            if result.get('status') == 'success':
                if self.toast_notifications:
                    agent_name = result.get('agent', 'агент')
                    self.toast_notifications.show_toast(
                        "JARVIS Agent",
                        f"Задача выполнена: {result.get('message', 'успешно')}",
                        duration=5000
                    )

                files = result.get('files', {})
                if files:
                    self.logger.info(f"Создано файлов: {len(files)}")

                return {
                    "status": "success",
                    "message": result.get('message', 'Задача выполнена'),
                    "agent": result.get('agent', 'Unknown'),
                    "files_created": len(files)
                }
            else:
                return {
                    "status": "error",
                    "message": result.get('message', 'Ошибка выполнения задачи')
                }

        except Exception as e:
            self.logger.error(f"Ошибка при обработке задачи агентом: {e}")
            return {
                "status": "error",
                "message": f"Ошибка: {str(e)}"
            }

    def process_command(self, text: str) -> Dict:
        """Обработка голосовой или текстовой команды."""
        self.logger.info(f"Получена команда: {text}")

        if self.hud:
            self.hud.set_status("PROCESSING")
            self.hud.set_voice_active(True)

        # Обработка команд управления агентами
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in ["какие агенты", "список агентов", "история задач", "возможности агента", "статус агента"]):
            return self._handle_agent_voice_command(text_lower)

        # Проверка ключевых слов для делегирования агентам
        agent_keywords = [
            "создай", "напиши", "разработай", "программ", "код",
            "сайт", "лендинг", "веб", "html", "css", "javascript", "react",
            "python", "sql", "скрипт", "функция", "класс", "алгоритм",
            "анализ", "данные", "статистика", "график", "визуализация", "отчет",
            "дизайн", "макет", "ui", "ux", "интерфейс", "стиль", "цвета", "svg", "графика", "иконка", "логотип", "оформление",
            "docker", "ci/cd", "развертывание", "деплой", "deploy", "автоматизация", "bash", "сервер", "nginx", "github actions", "инфраструктура"
        ]
        if any(keyword in text_lower for keyword in agent_keywords):
            return self._handle_agent_task(text_lower)

        # Стандартные команды
        if any(word in text_lower for word in ["привет", "здравствуй", "добрый день"]):
            return {"status": "ok", "message": "Приветствую! Чем могу помочь?", "text": text}

        if any(word in text_lower for word in ["погода", "температура"]):
            return self._handle_weather_command(text_lower)

        if any(word in text_lower for word in ["курс валют", "доллар", "евро", "рубль"]):
            return self._handle_currency_command(text_lower)

        if any(word in text_lower for word in ["новости", "что нового"]):
            return self._handle_news_command(text_lower)

        if any(word in text_lower for word in ["запусти", "открой"]):
            if self.app_launcher:
                return self.app_launcher.launch_app(text_lower)
            return {"status": "error", "message": "Модуль запуска приложений недоступен"}

        if any(word in text_lower for word in ["убери", "очисти"]):
            if self.clean_desktop:
                return self.clean_desktop.clean_desktop()
            return {"status": "error", "message": "Модуль очистки рабочего стола недоступен"}

        return {"status": "ok", "message": "Команда не распознана", "text": text}

    def _handle_weather_command(self, text: str) -> Dict:
        """Обработка команды погоды."""
        if not self.weather_module:
            return {"status": "error", "message": "Модуль погоды не загружен"}

        city = "Москва"
        cities = ["москва", "санкт-петербург", "питер", "новосибирск", "екатеринбург", "казань", "нижний новгород"]

        for c in cities:
            if c in text.lower():
                city = c.capitalize()
                break

        return self.weather_module.get_weather(city)

    def _handle_currency_command(self, text: str) -> Dict:
        """Обработка команды курса валют."""
        if not self.currency_module:
            return {"status": "error", "message": "Модуль валют не загружен"}
        return self.currency_module.get_rates()

    def _handle_news_command(self, text: str) -> Dict:
        """Обработка команды новостей."""
        if not self.news_module:
            return {"status": "error", "message": "Модуль новостей не загружен"}
        return self.news_module.get_news()

    def start(self):
        """Запуск системы JARVIS."""
        self.logger.info("Запуск JARVIS...")
        self.running = True

        # Загрузка плагинов
        self.plugin_manager.load_plugins()

        # Загрузка агентов
        self.agent_manager.initialize_agents()

        self.logger.info("JARVIS запущен и готов к работе")

        if self.toast_notifications:
            self.toast_notifications.show_toast("JARVIS", "Система запущена")

    def stop(self):
        """Остановка системы JARVIS."""
        self.logger.info("Остановка JARVIS...")
        self.running = False

        if self.toast_notifications:
            self.toast_notifications.show_toast("JARVIS", "Система остановлена")

        self.logger.info("JARVIS остановлен")

    def get_status(self) -> Dict:
        """Получить статус системы."""
        return {
            "running": self.running,
            "modules_loaded": len(self.modules),
            "plugins_loaded": len(self.plugin_manager.loaded),
            "agents_active": self.agent_manager.get_active_count()
        }
