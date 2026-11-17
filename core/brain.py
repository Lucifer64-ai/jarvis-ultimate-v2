"""JARVIS Brain - Главный контроллер и обработка команд"""

import logging
from typing import Dict, Optional

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

        # Модули
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

        # Новые модули
        self.voice_recognizer = None
        self.command_processor = None
        self.process_manager = None
        self.network_manager = None
        self.ml_engine = None
        self.llm_router = None

        # Проактивный ассистент
        self.proactive_assistant = None
        self.system_monitor = None
        self.smart_home = None
        self.macro_automation = None
        self.file_organizer = None
        self.face_recognition = None
        self.user_memory = None
        self.holographic_hud = None

        # Voice Personality
        self.voice_personality = None

        self.modules = {}
        self.running = False
        self.gui_enabled = self.config.get("ui.hud_enabled", True)
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

        # Process Manager
        try:
            from modules.process_manager import ProcessManager
            self.process_manager = ProcessManager(self)
            self.logger.info("Модуль Process Manager загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Process Manager: {e}")
            self.process_manager = None

        # Network Manager
        try:
            from modules.network_manager import NetworkManager
            self.network_manager = NetworkManager(self)
            self.logger.info("Модуль Network Manager загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Network Manager: {e}")
            self.network_manager = None

        # Mouse Control (управление мышкой)
        try:
            from modules.mouse_control import MouseControl
            self.mouse_control = MouseControl(self)
            self.logger.info("Модуль Mouse Control загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Mouse Control: {e}")
            self.mouse_control = None

        # Screen Analyzer (анализ экрана)
        try:
            from modules.screen_analyzer import ScreenAnalyzer
            self.screen_analyzer = ScreenAnalyzer(self)
            self.logger.info("Модуль Screen Analyzer загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Screen Analyzer: {e}")
            self.screen_analyzer = None

        # ML Engine (адаптивное обучение)
        try:
            from ai.adaptive_ml import AdaptiveMLEngine
            self.ml_engine = AdaptiveMLEngine(self)
            self.logger.info("Модуль ML Engine загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля ML Engine: {e}")
            self.ml_engine = None

        # Weather / Currency / News модули
        try:
            from modules.weather import WeatherModule
            self.weather_module = WeatherModule(self)
            self.logger.info("Модуль погоды загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля погоды: {e}")
            self.weather_module = None

        try:
            from modules.currency import CurrencyModule
            self.currency_module = CurrencyModule(self)
            self.logger.info("Модуль валют загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля валют: {e}")
            self.currency_module = None

        try:
            from modules.news import NewsModule
            self.news_module = NewsModule(self)
            self.logger.info("Модуль новостей загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля новостей: {e}")
            self.news_module = None


        # Инициализация LLM Router (OpenAI + Ollama)
        try:
            from ai.llm_router import LLMRouter
            self.llm_router = LLMRouter(self)
            self.logger.info("Модуль LLM Router загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки LLM Router: {e}")
            self.llm_router = None

        # Инициализация HUD
        try:
            from hud.jarvis_hud import JarvisHUD
            self.hud = JarvisHUD(self)
            self.logger.info("Модуль HUD загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки HUD: {e}")
            self.hud = None

        # Voice Personality
        try:
            from modules.voice_personality import VoicePersonality
            self.voice_personality = VoicePersonality(self)
            self.logger.info("Модуль Voice Personality загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Voice Personality: {e}")
            self.voice_personality = None

        # Proactive Assistant
        try:
            from modules.proactive_assistant import ProactiveAssistant
            self.proactive_assistant = ProactiveAssistant(self)
            self.logger.info("Модуль Proactive Assistant загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Proactive Assistant: {e}")
            self.proactive_assistant = None

        # System Monitor
        try:
            from modules.system_monitor import SystemMonitor
            self.system_monitor = SystemMonitor(self)
            self.logger.info("Модуль System Monitor загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля System Monitor: {e}")
            self.system_monitor = None

        # Smart Home
        try:
            from modules.smart_home import SmartHome
            self.smart_home = SmartHome(self)
            self.logger.info("Модуль Smart Home загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Smart Home: {e}")
            self.smart_home = None

        # Macro Automation
        try:
            from modules.macro_automation import MacroAutomation
            self.macro_automation = MacroAutomation(self)
            self.logger.info("Модуль Macro Automation загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Macro Automation: {e}")
            self.macro_automation = None

        # File Organizer
        try:
            from modules.file_organizer import FileOrganizer
            self.file_organizer = FileOrganizer(self)
            self.logger.info("Модуль File Organizer загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля File Organizer: {e}")
            self.file_organizer = None

        # Face Recognition
        try:
            from modules.face_recognition import FaceRecognition
            self.face_recognition = FaceRecognition(self)
            self.logger.info("Модуль Face Recognition загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Face Recognition: {e}")
            self.face_recognition = None

        # User Memory
        try:
            from modules.user_memory import UserMemory
            self.user_memory = UserMemory(self)
            self.logger.info("Модуль User Memory загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля User Memory: {e}")
            self.user_memory = None

        # Holographic HUD
        try:
            from ui.holographic_hud import HolographicHUD
            self.holographic_hud = HolographicHUD(self)
            self.logger.info("Модуль Holographic HUD загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля Holographic HUD: {e}")
            self.holographic_hud = None
    def _init_voice(self):
        """Инициализация голосовых модулей."""
        # Voice Speaker (синтез речи)
        try:
            from voice.speaker import VoiceSpeaker
            self.voice_speaker = VoiceSpeaker(self)
            self.logger.info("Модуль синтеза речи загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля синтеза речи: {e}")
            self.voice_speaker = None

        # Voice Recognizer (распознавание речи)
        try:
            from voice.recognizer import VoiceRecognizer
            self.voice_recognizer = VoiceRecognizer(self)
            self.logger.info("Модуль распознавания речи загружен")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля распознавания речи: {e}")
            self.voice_recognizer = None

        # Command Processor (обработка команд)
        try:
            from voice.command_processor import CommandProcessor
            self.command_processor = CommandProcessor(self)
            self.logger.info("Модуль обработки команд загружен")

            # Подключаем callbacks
            if self.voice_recognizer:
                self.voice_recognizer.on_speech_detected = self._on_speech_detected
                self.voice_recognizer.on_command_recognized = self._on_command_recognized
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модуля обработки команд: {e}")
            self.command_processor = None

    def _on_speech_detected(self, text: str):
        """Callback при обнаружении речи."""
        self.logger.info(f"Обнаружена речь: {text}")
        if self.toast_notifications:
            self.toast_notifications.show_toast("JARVIS", f"Слышу: {text[:50]}...")

    def _on_command_recognized(self, text: str, result: Dict):
        """Callback при распознавании команды."""
        self.logger.info(f"Команда распознана: {text} -> {result}")
        if self.voice_speaker and result.get("message"):
            self.voice_speaker.speak(result.get("message"))

    def execute_action(self, action: str) -> Dict:
        """Выполнение действия по имени (для CommandProcessor)."""
        self.logger.info(f"Выполнение действия: {action}")

        parts = action.split(".")
        if len(parts) != 2:
            return {"status": "error", "message": f"Неверный формат действия: {action}"}

        module_name, method_name = parts

        # Маршрутизация к модулям
        if module_name == "system":
            if self.windows_integration:
                method = getattr(self.windows_integration, method_name, None)
                if method:
                    return method()
            return {"status": "error", "message": "Модуль system недоступен"}

        elif module_name == "desktop":
            if self.clean_desktop:
                method = getattr(self.clean_desktop, method_name, None)
                if method:
                    return method()
            return {"status": "error", "message": "Модуль desktop недоступен"}

        elif module_name == "voice":
            if self.voice_recognizer:
                method = getattr(self.voice_recognizer, method_name, None)
                if method:
                    return method()
            return {"status": "error", "message": "Модуль voice недоступен"}

        elif module_name == "info":
            if method_name == "get_time":
                from datetime import datetime
                now = datetime.now()
                return {"status": "ok", "message": f"Сейчас {now.strftime('%H:%M')}"}
            elif method_name == "get_date":
                from datetime import datetime
                now = datetime.now()
                return {"status": "ok", "message": f"Сегодня {now.strftime('%d.%m.%Y')}"}
            elif method_name == "get_weather":
                if self.weather_module:
                    return self.weather_module.get_weather("Москва")
                return {"status": "error", "message": "Модуль погоды недоступен"}
            return {"status": "error", "message": f"Неизвестное действие: {action}"}

        elif module_name == "app":
            if self.app_launcher:
                if method_name == "open_notepad":
                    return self.app_launcher.launch("блокнот")
                elif method_name == "open_calculator":
                    return self.app_launcher.launch("калькулятор")
                elif method_name == "open_browser":
                    return self.app_launcher.launch("браузер")
            return {"status": "error", "message": "Модуль app недоступен"}

        elif module_name == "process":
            if self.process_manager:
                method = getattr(self.process_manager, method_name, None)
                if method:
                    return method()
            return {"status": "error", "message": "Модуль process недоступен"}

        elif module_name == "network":
            if self.network_manager:
                method = getattr(self.network_manager, method_name, None)
                if method:
                    return method()
            return {"status": "error", "message": "Модуль network недоступен"}

        return {"status": "error", "message": f"Неизвестный модуль: {module_name}"}

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

        # Сначала пробуем CommandProcessor (с ML)
        if self.command_processor:
            result = self.command_processor.process(text)
            if result.get("status") != "unknown":
                return result

        # Обработка команд управления агентами
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in ["какие агенты", "список агентов", "история задач", "возможности агента", "статус агента"]):
            return self._handle_agent_voice_command(text_lower)

        # === Mouse Control (проверяем до agent keywords, т.к. "размер экрана" может пересекаться) ===
        if any(word in text_lower for word in ["курсор", "мышь", "клик", "прокрут", "scroll", "кликни", "кликай", "размер экрана", "разрешение"]):
            return self._handle_mouse_command(text_lower)

        # === Screen Analyzer (проверяем до agent keywords, т.к. "анализ экрана" пересекается с "анализ") ===
        if any(word in text_lower for word in ["скриншот", "снимок экрана", "анализ экрана", "распознай текст", "найди текст", "прочти текст", "что на экране", "цвет пикселя"]):
            return self._handle_screen_command(text_lower)

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
                return self.app_launcher.launch(text_lower)
            return {"status": "error", "message": "Модуль запуска приложений недоступен"}

        if any(word in text_lower for word in ["убери", "очисти"]):
            if self.clean_desktop:
                return self.clean_desktop.enable_clean_mode()
            return {"status": "error", "message": "Модуль очистки рабочего стола недоступен"}


        # Автоматическая передача нераспознанных команд в ChatGPT
        if self.llm_router:
            self.logger.info("Команда не распознана локально, передаю в ChatGPT...")
            return self.llm_router.chat(text)

        return {"status": "ok", "message": "Команда не распознана", "text": text}

    def _handle_mouse_command(self, text: str) -> Dict:
        """Обработка команд управления мышкой."""
        if not self.mouse_control:
            return {"status": "error", "message": "Модуль управления мышкой недоступен"}

        # Перемещение в центр
        if any(w in text for w in ["центр", "center"]):
            return self.mouse_control.center_cursor()

        # Получение позиции
        if any(w in text for w in ["где курсор", "позиция курсора", "координаты"]):
            return self.mouse_control.get_position()

        # Размер экрана
        if any(w in text for w in ["размер экрана", "разрешение"]):
            return self.mouse_control.get_screen_size()

        # Прокрутка вверх
        if any(w in text for w in ["прокрути вверх", "scroll up", "колесо вверх"]):
            return self.mouse_control.scroll_up()

        # Прокрутка вниз
        if any(w in text for w in ["прокрути вниз", "scroll down", "колесо вниз"]):
            return self.mouse_control.scroll_down()

        # Клик (по умолчанию левый клик в текущей позиции)
        if any(w in text for w in ["клик", "click"]):
            if "прав" in text:
                return self.mouse_control.right_click()
            if "двойн" in text:
                return self.mouse_control.double_click()
            return self.mouse_control.click()

        # Помощь по мыши
        if any(w in text for w in ["помощь мышь", "что можешь мышь"]):
            return {
                "status": "ok",
                "message": "Управление мышкой: клик, правый клик, двойной клик, прокрутка вверх/вниз, перемести курсор в центр, где курсор, размер экрана"
            }

        return {"status": "error", "message": "Команда мыши не распознана. Попробуйте: клик, прокрути вверх, где курсор"}

    def _handle_screen_command(self, text: str) -> Dict:
        """Обработка команд анализа экрана."""
        if not self.screen_analyzer:
            return {"status": "error", "message": "Модуль анализа экрана недоступен"}

        # Полный анализ экрана
        if any(w in text for w in ["анализ экрана", "что на экране", "проанализируй экран"]):
            return self.screen_analyzer.analyze_screen()

        # Скриншот
        if any(w in text for w in ["скриншот", "снимок экрана", "сделай скриншот"]):
            return self.screen_analyzer.capture_full_screen()

        # Распознать текст
        if any(w in text for w in ["распознай текст", "прочти текст", "текст на экране"]):
            return self.screen_analyzer.read_screen_text()

        # Найти текст
        if "найди текст" in text or "найти текст" in text:
            target = text.replace("найди текст", "").replace("найти текст", "").strip() or "вход"
            return self.screen_analyzer.find_text_on_screen(target)

        # Клик по тексту
        if "кликни по тексту" in text or "клик по тексту" in text:
            target = text.replace("кликни по тексту", "").replace("клик по тексту", "").strip() or "вход"
            return self.screen_analyzer.click_on_text(target)

        # Цвет пикселя (требует координат, просто вернём инструкцию)
        if "цвет пикселя" in text:
            return {
                "status": "ok",
                "message": "Укажите координаты: цвет пикселя X Y (например: цвет пикселя 100 200)"
            }

        # Помощь по экрану
        if any(w in text for w in ["помощь экран", "что можешь экран"]):
            return {
                "status": "ok",
                "message": "Анализ экрана: скриншот, анализ экрана, распознай текст, найди текст <слово>, кликни по тексту <слово>, цвет пикселя X Y"
            }

        return {"status": "error", "message": "Команда экрана не распознана. Попробуйте: скриншот, анализ экрана, распознай текст"}

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

        # Запуск голосового распознавания
        if self.voice_recognizer:
            self.voice_recognizer.start_listening()

        self.logger.info("JARVIS запущен и готов к работе")

        if self.toast_notifications:
            self.toast_notifications.show_toast("JARVIS", "Система запущена")

    def stop(self):
        """Остановка системы JARVIS."""
        self.logger.info("Остановка JARVIS...")
        self.running = False

        # Остановка голосового распознавания
        if self.voice_recognizer:
            self.voice_recognizer.stop_listening()

        if self.toast_notifications:
            self.toast_notifications.show_toast("JARVIS", "Система остановлена")

        self.logger.info("JARVIS остановлен")

    def get_status(self) -> Dict:
        """Получить статус системы."""
        return {
            "running": self.running,
            "modules_loaded": len(self.modules),
            "plugins_loaded": len(self.plugin_manager.loaded),
            "agents_active": self.agent_manager.get_active_count(),
            "voice_recognizer": self.voice_recognizer is not None,
            "command_processor": self.command_processor is not None,
            "process_manager": self.process_manager is not None,
            "network_manager": self.network_manager is not None,
            "ml_engine": self.ml_engine is not None
        }

    def initialize(self):
        """Публичная обёртка для инициализации модулей (совместимость с main.py)."""
        self._init_modules()
