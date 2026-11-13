"""
¡и½µ· µи JARVIS
"""

import pyttsx3
from typing import Optional


class VoiceSpeaker:
    """¡и½µ· µи."""

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
        """¾и·½µи µº."""
        try:
            self.brain.logger.info(f"¾в¾: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.brain.logger.error(f"и±º° и½µ·° µи: {e}")

    def set_rate(self, rate: int):
        """£°½¾ви º¾¾ µи."""
        self.engine.setProperty('rate', rate)

    def set_volume(self, volume: float):
        """£°½¾ви ³¾¼º¾."""
        self.engine.setProperty('volume', volume)
