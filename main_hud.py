"""
JARVIS Ultimate - ¢¾º° в¾´°  HUD и½µµ¹¾¼
"""

import sys
import time
from PyQt5.QtWidgets import QApplication
from core.brain import JarvisBrain
from hud.holographic_ui import HolographicHUD


def main():
    """»°в½° ½ºи."""
    print("=" * 50)
    print("  JARVIS Ultimate v2.0.0")
    print("  Holographic HUD Interface")
    print("=" * 50)
    print()
    
    # ¡¾·´°½иµ Qt голосов
    app = QApplication(sys.argv)
    
    # ½ии°»и·°и JARVIS Brain
    brain = JarvisBrain()
    
    try:
        # ½ии°»и·°и вµ ¼¾´»µ¹
        brain.initialize()
        
        # ¡¾·´°½иµ HUD и½µµ¹°
        hud = HolographicHUD(brain)
        brain.hud = hud
        
        # °¿º
        brain.start()
        
        print("\nJARVIS ³¾¾в º °±¾µ.")
        print("HUD и½µµ¹ °ºивµ½.")
        print("°в¹ º»иº ½° HUD - ·°º и½µµ¹.")
        print()
        
        # °¿º Qt event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"ииµº° ¾и±º°: {e}")
        sys.exit(1)
    
    finally:
        brain.stop()
        print("\n¾ ви´°½и!")


if __name__ == "__main__":
    main()
