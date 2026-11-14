"""
#JARVIS Ultimate - Полнофункциональный AI-ассистент
"""

import sys
import time

# Настройка пути для импорта модулей PyInstaller
import dotenv
from dotenv import load_dotenv

from core.brain import JarvisBrain
from ui.settings_window import show_settings_window


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
        sys.exit(0)

    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        brain.stop()
        sys.exit(1)


if __name__ == "__main__":
    # Загрузка переменных окружения
    load_dotenv()

    # Запуск приложения
    main()
