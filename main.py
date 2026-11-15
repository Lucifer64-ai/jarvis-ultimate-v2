"""
#JARVIS Ultimate - Полнофункциональный AI-ассистент
"""

import sys
import time
import threading
import asyncio

# Настройка пути для импорта модулей PyInstaller
from dotenv import load_dotenv

from core.brain import JarvisBrain
from core.websocket_server import create_websocket_server
from core.qr_connection import create_qr_connection_manager
from ui.settings_window import show_settings_window

# Новые модули
from ai.vision import VisionModule
from ai.pixel_eyes import PixelEyes
from ai.wake_word import WakeWordDetector
from ai.browser_automation import BrowserAutomation
from ai.hybrid_intent import HybridIntentSystem
from ai.confirmation_shell import ConfirmationShell
from ai.subagent_orchestration import SubAgentOrchestrator
from ai.streaming_tts import StreamingTTS
from ai.live_dashboard import LiveDashboard
from ai.plugin_ecosystem import PluginEcosystem


def main():
    """Главная функция запуска JARVIS."""
    print("=" * 50)
    print("  JARVIS Ultimate v2.0.0")
    print("  AI Assistant with Learning Capabilities")
    print("=" * 50)
    print()

    # Инициализация JARVIS
    brain = JarvisBrain()

    try:
        # Инициализация всех модулей и подсистем
        brain.initialize()

        # Инициализация QR-подключения
        brain.qr_connection = create_qr_connection_manager(brain)

        # Запуск WebSocket сервера в отдельном потоке
        def start_websocket_server():
            """Запуск WebSocket сервера в отдельном потоке."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ws_server = create_websocket_server(brain)
            loop.run_until_complete(ws_server.start())

        ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
        ws_thread.start()
        print("✅ WebSocket сервер запущен (порт 8765)")
        print("📱 Мобильное приложение может подключиться через QR-код")

        # Инициализация новых модулей
        print("\n🚀 Инициализация новых модулей...")

        # Vision Module
        try:
            brain.vision = VisionModule(api_key=brain.config.get('OPENAI_API_KEY', ''))
            print("✅ Vision Module инициализирован")
        except Exception as e:
            print(f"⚠️ Vision Module не инициализирован: {e}")

        # Pixel Eyes
        try:
            brain.pixel_eyes = PixelEyes()
            print("✅ Pixel Eyes инициализирован")
        except Exception as e:
            print(f"⚠️ Pixel Eyes не инициализирован: {e}")

        # Wake Word Detector
        try:
            brain.wake_word_detector = WakeWordDetector()
            print("✅ Wake Word Detector инициализирован")
        except Exception as e:
            print(f"⚠️ Wake Word Detector не инициализирован: {e}")

        # Browser Automation
        try:
            brain.browser = BrowserAutomation()
            print("✅ Browser Automation инициализирован")
        except Exception as e:
            print(f"⚠️ Browser Automation не инициализирован: {e}")

        # Hybrid Intent System
        try:
            brain.hybrid_intent = HybridIntentSystem(ai_fallback=brain.process_command)
            print("✅ Hybrid Intent System инициализирован")
        except Exception as e:
            print(f"⚠️ Hybrid Intent System не инициализирован: {e}")

        # Confirmation Shell
        try:
            brain.confirmation_shell = ConfirmationShell()
            print("✅ Confirmation Shell инициализирован")
        except Exception as e:
            print(f"⚠️ Confirmation Shell не инициализирован: {e}")

        # Sub-Agent Orchestration
        try:
            brain.orchestrator = SubAgentOrchestrator()
            print("✅ Sub-Agent Orchestration инициализирован")
        except Exception as e:
            print(f"⚠️ Sub-Agent Orchestration не инициализирован: {e}")

        # Streaming TTS
        try:
            brain.streaming_tts = StreamingTTS(api_key=brain.config.get('OPENAI_API_KEY', ''))
            print("✅ Streaming TTS инициализирован")
        except Exception as e:
            print(f"⚠️ Streaming TTS не инициализирован: {e}")

        # Live Dashboard
        try:
            brain.dashboard = LiveDashboard()
            # Запуск Dashboard в отдельном потоке
            dashboard_thread = threading.Thread(target=brain.dashboard.start, daemon=True)
            dashboard_thread.start()
            print("✅ Live Dashboard запущен (порт 8000)")
        except Exception as e:
            print(f"⚠️ Live Dashboard не инициализирован: {e}")

        # Plugin Ecosystem
        try:
            brain.plugins = PluginEcosystem()
            print("✅ Plugin Ecosystem инициализирован")
        except Exception as e:
            print(f"⚠️ Plugin Ecosystem не инициализирован: {e}")

        # Запуск основного цикла
        brain.start()

        # Запуск GUI в отдельном потоке
        if brain.gui_enabled:
            from ui.main_window import MainWindow
            window = MainWindow(brain)
            window.show()

        # Основной цикл обработки команд
        print("\nJARVIS запущен. Готов к работе.")
        print("Нажмите Ctrl+C для завершения.\n")

        while brain.running:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nПолучен сигнал завершения...")
        brain.stop()
        print("JARVIS остановлен.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        brain.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
