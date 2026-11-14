"""
JARVIS Ultimate - Запуск с HUD интерфейсом
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.brain import JarvisBrain
from hud.jarvis_hud import JarvisHUD


def main():
    """Главная функция запуска JARVIS с HUD."""
    print("=" * 60)
    print("🤖 JARVIS Ultimate - Запуск с HUD интерфейсом")
    print("=" * 60)

    # Инициализация brain
    print("\n🧠 Инициализация JARVIS Brain...")
    brain = JarvisBrain()

    # Проверка модулей
    print("\n📦 Проверка модулей:")
    modules_status = {
        "Voice Recognizer": brain.voice_recognizer is not None,
        "Command Processor": brain.command_processor is not None,
        "Process Manager": brain.process_manager is not None,
        "Network Manager": brain.network_manager is not None,
        "ML Engine": brain.ml_engine is not None,
        "ChatGPT": brain.chatgpt is not None,
    }

    for module, status in modules_status.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {module}")

    # Запуск системы
    print("\n🚀 Запуск JARVIS...")
    brain.start()

    # Создание Qt приложения
    print("\n🎨 Запуск HUD интерфейса...")
    app = QApplication(sys.argv)

    # Создание HUD окна
    hud = JarvisHUD(brain)
    hud.show()

    # Подключение голосового управления к HUD
    if brain.voice_recognizer:
        def on_speech_detected(text):
            hud.show_command(text, "Обработка...")
            hud.set_status("PROCESSING")

        def on_command_recognized(text, result):
            response = result.get("message", "Выполнено")
            hud.show_command(text, response)
            hud.set_status("READY")

            # Озвучивание ответа
            if brain.voice_speaker:
                brain.voice_speaker.speak(response)

        brain.voice_recognizer.on_speech_detected = on_speech_detected
        brain.voice_recognizer.on_command_recognized = on_command_recognized

        # Начинаем слушать
        brain.voice_recognizer.start_listening()
        print("🎤 Голосовое управление активно")

    # Обновление статуса в HUD
    hud.set_status("READY")

    print("\n✅ JARVIS готов к работе!")
    print("   Скажите 'Джарвис' для активации")
    print("   Или введите команду в консоль")
    print("\n   Нажмите Ctrl+C для выхода")
    print("=" * 60)

    # Запуск event loop
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\n\n⏹️  Остановка JARVIS...")
        brain.stop()
        print("✅ JARVIS остановлен")


if __name__ == "__main__":
    main()
