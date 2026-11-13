"""
JARVIS Ultimate - ¢¾º° ²¾´°  HUD ¸½µµ¹¾¼
"""

import sys
import time
from PyQt5.QtWidgets import QApplication
from core.brain import JarvisBrain
from hud.holographic_ui import HolographicHUD


def main():
    """»°²½° ½º¸."""
    print("=" * 50)
    print("  JARVIS Ultimate v2.0.0")
    print("  Holographic HUD Interface")
    print("=" * 50)
    print()
    
    # ¡¾·´°½¸µ Qt ¿¸»¾¶µ½¸
    app = QApplication(sys.argv)
    
    # ½¸¸°»¸·°¸ JARVIS Brain
    brain = JarvisBrain()
    
    try:
        # ½¸¸°»¸·°¸ ²µ ¼¾´»µ¹
        brain.initialize()
        
        # ¡¾·´°½¸µ HUD ¸½µµ¹°
        hud = HolographicHUD(brain)
        brain.hud = hud
        
        # °¿º
        brain.start()
        
        print("\nJARVIS ³¾¾² º °±¾µ.")
        print("HUD ¸½µµ¹ °º¸²µ½.")
        print("°²¹ º»¸º ½° HUD - ·°º ¸½µµ¹.")
        print()
        
        # °¿º Qt event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"¸¸µº° ¾¸±º°: {e}")
        sys.exit(1)
    
    finally:
        brain.stop()
        print("\n¾ ²¸´°½¸!")


if __name__ == "__main__":
    main()
