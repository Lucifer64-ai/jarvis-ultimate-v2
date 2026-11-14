"""
Скрипт установки контекстного меню JARVIS в проводнике Windows
"""

import winreg
import sys
import os
from pathlib import Path


def install_context_menu():
    """Установка контекстного меню."""
    try:
        # Путь к JARVIS
        jarvis_path = sys.executable

        # Для файлов
        file_key = r"*\shell\JARVIS"
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, file_key) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "JARVIS - открыть файл")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, jarvis_path)

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{file_key}\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{jarvis_path}" open "%1"')

        # Для папок
        folder_key = r"Directory\shell\JARVIS"
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, folder_key) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "JARVIS - открыть папку")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, jarvis_path)

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{folder_key}\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{jarvis_path}" open "%1"')

        print("Контекстное меню JARVIS успешно установлено в систему")
        return 0

    except Exception as e:
        print(f"Ошибка установки контекстного меню: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(install_context_menu())
