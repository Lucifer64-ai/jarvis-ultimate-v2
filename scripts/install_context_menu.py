"""
¡º¸¿ °½¾²º¸ º¾½µº½¾³¾ ¼µ½ ¿¾²¾´½¸º° Windows
"""

import winreg
import sys
import os
from pathlib import Path


def install_context_menu():
    """£°½¾²º° º¾½µº½¾³¾ ¼µ½."""
    try:
        #  º JARVIS
        jarvis_path = sys.executable
        
        # » °¹»¾²
        file_key = r"*\shell\JARVIS"
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, file_key) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "JARVIS - º °¹»")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, jarvis_path)
        
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{file_key}\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{jarvis_path}" open "%1"')
        
        # » ¿°¿¾º
        folder_key = r"Directory\shell\JARVIS"
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, folder_key) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "JARVIS - º ¿°¿º")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, jarvis_path)
        
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{folder_key}\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{jarvis_path}" open "%1"')
        
        print("¾½µº½¾µ ¼µ½ °½¾²»µ½¾ ¿µ½¾")
        return 0
    
    except Exception as e:
        print(f"¸±º° °½¾²º¸ º¾½µº½¾³¾ ¼µ½: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(install_context_menu())
