"""
¡¸½µ· µ¸ JARVIS
"""

import pyttsx3
from typing import Optional


class VoiceSpeaker:
    """¡¸½µ· µ¸."""

    def __init__(self, brain):
        self.brain = brain
        self.engine = pyttsx3.init()
        
        # °¾¹º° ³¾»¾°
        voice_config = brain.config.get("voice", {})
        self.engine.setProperty('rate', voice_config.get("rate", 180))
        self.engine.setProperty('volume', voice_config.get("volume", 1.0))
        
        # ±¾ º¾³¾ ³¾»¾°
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'russian' in voice.name.lower() or 'ru' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text: str):
        """¾¸·½µ¸ µº."""
        try:
            self.brain.logger.info(f"¾²¾: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.brain.logger.error(f"¸±º° ¸½µ·° µ¸: {e}")

    def set_rate(self, rate: int):
        """£°½¾²¸ º¾¾ µ¸."""
        self.engine.setProperty('rate', rate)

    def set_volume(self, volume: float):
        """£°½¾²¸ ³¾¼º¾."""
        self.engine.setProperty('volume', volume)
