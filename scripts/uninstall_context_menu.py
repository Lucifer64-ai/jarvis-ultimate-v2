"""
¡ºи¿ ´°»µ½и º¾½µº½¾³¾ ¼µ½ ¿¾в¾´½иº° Windows
"""

import winreg
import sys


def uninstall_context_menu():
    """£´°»µ½иµ º¾½µº½¾³¾ ¼µ½."""
    try:
        # £´°»µ½иµ ´» °¹»¾в
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\JARVIS\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\JARVIS")
        except:
            pass
        
        # £´°»µ½иµ ´» ¿°¿¾º
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\JARVIS\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\JARVIS")
        except:
            pass
        
        print("¾½µº½¾µ ¼µ½ ´°»µ½¾ ¿µ½¾")
        return 0
    
    except Exception as e:
        print(f"и±º° ´°»µ½и º¾½µº½¾³¾ ¼µ½: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(uninstall_context_menu())
