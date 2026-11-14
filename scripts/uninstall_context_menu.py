"""
Скрипт удаления контекстного меню JARVIS из проводника Windows
"""

import winreg
import sys


def uninstall_context_menu():
    """Удаление контекстного меню."""
    try:
        # Удаление для файлов
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\JARVIS\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\JARVIS")
        except:
            pass

        # Удаление для папок
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\JARVIS\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\JARVIS")
        except:
            pass

        print("Контекстное меню JARVIS удалено из системы")
        return 0

    except Exception as e:
        print(f"Ошибка удаления контекстного меню: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(uninstall_context_menu())
