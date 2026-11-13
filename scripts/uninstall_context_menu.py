"""
¡º¸¿ ´°»µ½¸ º¾½µº½¾³¾ ¼µ½ ¿¾²¾´½¸º° Windows
"""

import winreg
import sys


def uninstall_context_menu():
    """£´°»µ½¸µ º¾½µº½¾³¾ ¼µ½."""
    try:
        # £´°»µ½¸µ ´» °¹»¾²
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\JARVIS\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\JARVIS")
        except:
            pass
        
        # £´°»µ½¸µ ´» ¿°¿¾º
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\JARVIS\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\JARVIS")
        except:
            pass
        
        print("¾½µº½¾µ ¼µ½ ´°»µ½¾ ¿µ½¾")
        return 0
    
    except Exception as e:
        print(f"¸±º° ´°»µ½¸ º¾½µº½¾³¾ ¼µ½: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(uninstall_context_menu())
