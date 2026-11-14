"""
JARVIS Ultimate - Точка входа с HUD интерфейсом
"""

import sys
import time
from PyQt5.QtWidgets import QApplication
from core.brain import JarvisBrain
from hud.holographic_ui import HolographicHUD


def main():
    """Главная функция запуска."""
    print("=" * 50)
    print("  JARVIS Ultimate v2.0.0")
    print("  Holographic HUD Interface")
    print("=" * 50)
    print()

    # Создание Qt приложения
    app = QApplication(sys.argv)

    # Инициализация JARVIS Brain
    brain = JarvisBrain()

    try:
        # Инициализация всех модулей
        brain.initialize()

        # Создание HUD интерфейса
        hud = HolographicHUD(brain)
        brain.hud = hud

        # Запуск
        brain.start()

        print("\nJARVIS готов к работе.")
        print("HUD интерфейс активен.")
        print("Правый клик на HUD - закрыть интерфейс.")
        print()

        # Запуск Qt event loop
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)

    finally:
        brain.stop()
        print("\nДо свидания!")


if __name__ == "__main__":
    main()
