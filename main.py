"""
#JARVIS Ultimate - Полнофункциональный AI-ассистент
"""

import sys
import time
import threading
import asyncio
import os

# Настройка пути для импорта модулей PyInstaller
from dotenv import load_dotenv

from core.brain import JarvisBrain
from core.websocket_server import create_websocket_server
from core.qr_connection import create_qr_connection_manager


def enable_windows_autostart():
    """Включить автозапуск JARVIS при включении ПК (Windows)."""
    if os.name != "nt":
        return
    try:
        import winreg
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        exe_path = os.path.abspath(sys.argv[0])
        # Если это скрипт, добавляем python и путь к main.py
        if exe_path.endswith(".py"):
            exe_path = f'"{sys.executable}" "{exe_path}"'
        else:
            exe_path = f'"{exe_path}"'

        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, "JARVIS", 0, winreg.REG_SZ, exe_path)
        print("✅ Автозапуск JARVIS при включении ПК включён")
    except Exception as e:
        print(f"⚠️ Не удалось включить автозапуск: {e}")


def main():
    """Главная функция запуска JARVIS."""
    print("=" * 50)
    print("  JARVIS Ultimate v2.0.0")
    print("  AI Assistant with Learning Capabilities")
    print("=" * 50)
    print()

    # Включаем автозапуск при включении ПК (Windows)
    enable_windows_autostart()

    # Инициализация JARVIS
    brain = JarvisBrain()

    try:
        # Инициализация всех модулей и подсистем
        brain._init_modules()

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

        # Инициализация новых модулей (ленивые импорты —Some модули требуют Windows-специфичных библиотек)
        print("\n🚀 Инициализация новых модулей...")

        # Vision Module
        try:
            from ai.vision import VisionModule
            brain.vision = VisionModule(api_key=brain.config.get('OPENAI_API_KEY', ''))
            print("✅ Vision Module инициализирован")
        except Exception as e:
            print(f"⚠️ Vision Module не инициализирован: {e}")

        # Pixel Eyes
        try:
            from ai.pixel_eyes import PixelEyes
            brain.pixel_eyes = PixelEyes()
            print("✅ Pixel Eyes инициализирован")
        except Exception as e:
            print(f"⚠️ Pixel Eyes не инициализирован: {e}")

        # Wake Word Detector
        try:
            from ai.wake_word import WakeWordDetector
            brain.wake_word_detector = WakeWordDetector()
            print("✅ Wake Word Detector инициализирован")
        except Exception as e:
            print(f"⚠️ Wake Word Detector не инициализирован: {e}")

        # Browser Automation
        try:
            from ai.browser_automation import BrowserAutomation
            brain.browser = BrowserAutomation()
            print("✅ Browser Automation инициализирован")
        except Exception as e:
            print(f"⚠️ Browser Automation не инициализирован: {e}")

        # Hybrid Intent System
        try:
            from ai.hybrid_intent import HybridIntentSystem
            brain.hybrid_intent = HybridIntentSystem(ai_fallback=brain.process_command)
            print("✅ Hybrid Intent System инициализирован")
        except Exception as e:
            print(f"⚠️ Hybrid Intent System не инициализирован: {e}")

        # Confirmation Shell
        try:
            from ai.confirmation_shell import ConfirmationShell
            brain.confirmation_shell = ConfirmationShell()
            print("✅ Confirmation Shell инициализирован")
        except Exception as e:
            print(f"⚠️ Confirmation Shell не инициализирован: {e}")

        # Sub-Agent Orchestration
        try:
            from ai.subagent_orchestration import SubAgentOrchestrator
            brain.orchestrator = SubAgentOrchestrator()
            print("✅ Sub-Agent Orchestration инициализирован")
        except Exception as e:
            print(f"⚠️ Sub-Agent Orchestration не инициализирован: {e}")

        # Streaming TTS
        try:
            from ai.streaming_tts import StreamingTTS
            brain.streaming_tts = StreamingTTS(api_key=brain.config.get('OPENAI_API_KEY', ''))
            print("✅ Streaming TTS инициализирован")
        except Exception as e:
            print(f"⚠️ Streaming TTS не инициализирован: {e}")

        # Live Dashboard
        try:
            from ai.live_dashboard import LiveDashboard
            brain.dashboard = LiveDashboard()
            # Запуск Dashboard в отдельном потоке
            dashboard_thread = threading.Thread(target=brain.dashboard.start, daemon=True)
            dashboard_thread.start()
            print("✅ Live Dashboard запущен (порт 8000)")
        except Exception as e:
            print(f"⚠️ Live Dashboard не инициализирован: {e}")

        # Plugin Ecosystem
        try:
            from ai.plugin_ecosystem import PluginEcosystem
            brain.plugins = PluginEcosystem()
            print("✅ Plugin Ecosystem инициализирован")
        except Exception as e:
            print(f"⚠️ Plugin Ecosystem не инициализирован: {e}")

        # === Новые модули JARVIS ===
        # Proactive Assistant (утренний доклад, напоминания, системные алерты)
        try:
            if brain.proactive_assistant:
                brain.proactive_assistant.start()
                print("✅ Proactive Assistant запущен")
        except Exception as e:
            print(f"⚠️ Proactive Assistant не запущен: {e}")

        # System Monitor (CPU, RAM, диск, температура, сеть)
        try:
            if brain.system_monitor:
                brain.system_monitor.start()
                print("✅ System Monitor запущен")
        except Exception as e:
            print(f"⚠️ System Monitor не запущен: {e}")

        # Holographic HUD (полноэкранный overlay)
        try:
            if brain.holographic_hud:
                brain.holographic_hud.start()
                print("✅ Holographic HUD запущен")
        except Exception as e:
            print(f"⚠️ Holographic HUD не запущен: {e}")

        # Face Recognition (пробуждение по лицу)
        try:
            if brain.face_recognition and brain.face_recognition.enabled:
                brain.face_recognition.start()
                print("✅ Face Recognition запущен")
        except Exception as e:
            print(f"⚠️ Face Recognition не запущен: {e}")

        # File Organizer (наблюдение за папкой загрузок)
        try:
            if brain.file_organizer and brain.file_organizer.auto_organize:
                brain.file_organizer.start_watching()
                print("✅ File Organizer запущен (авто-организация)")
        except Exception as e:
            print(f"⚠️ File Organizer не запущен: {e}")

        # Smart Home (Home Assistant / MQTT)
        try:
            if brain.smart_home and brain.smart_home.enabled:
                print("✅ Smart Home инициализирован")
        except Exception as e:
            print(f"⚠️ Smart Home не инициализирован: {e}")

        # Macro Automation, User Memory — не требуют фонового запуска
        try:
            if brain.macro_automation:
                print("✅ Macro Automation инициализирован")
        except Exception as e:
            print(f"⚠️ Macro Automation не инициализирован: {e}")

        try:
            if brain.user_memory:
                print("✅ User Memory инициализирован")
        except Exception as e:
            print(f"⚠️ User Memory не инициализирован: {e}")

        # Запуск основного цикла
        brain.start()

        # Запуск графического интерфейса JARVIS (живое окно с анимациями)
        if brain.gui_enabled:
            try:
                from ui.main_window import run_interface
                # GUI запускается в основном потоке (Qt требует это)
                # Но мы уже в основном потоке, поэтому запускаем окно
                # и comando цикл в отдельном потоке
                print("\n🖥️ Запуск графического интерфейса JARVIS...")

                # Запускаем командный цикл в фоновом потоке
                def command_loop():
                    while brain.running:
                        time.sleep(0.1)

                cmd_thread = threading.Thread(target=command_loop, daemon=True)
                cmd_thread.start()

                # Запускаем GUI ( bloqueет основной поток, как и должно быть для Qt )
                run_interface(brain)

            except ImportError as e:
                print(f"⚠️ MainWindow недоступен: {e}")
                print("   Проверьте установку PyQt5: pip install PyQt5")
                # Fallback: консольный цикл
                print("\nJARVIS запущен в консольном режиме. Готов к работе.")
                print("Нажмите Ctrl+C для завершения.\n")
                while brain.running:
                    time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Ошибка запуска GUI: {e}")
                import traceback
                traceback.print_exc()
        else:
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
