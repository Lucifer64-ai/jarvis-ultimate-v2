"""
 °¿¾·½°в°½иµ µи JARVIS
"""

import speech_recognition as sr
from typing import Optional, Dict


class VoiceListener:
    """ °¿¾·½°в°½иµ ³¾»¾¾в º¾¼°½´."""

    def __init__(self, brain):
        self.brain = brain
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.wake_word = brain.config.get("voice", {}).get("wake_word", "´¶°ви")
        
        # °¾¹º° °¿¾·½°в°½и
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300

    def listen(self) -> Optional[str]:
        """¡»° и °¿¾·½° µ."""
        try:
            with self.microphone as source:
                self.brain.logger.info("¡»°...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

            self.brain.logger.info(" °¿¾·½° µ...")
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            self.brain.logger.info(f" °¿¾·½°½¾: {text}")
            return text

        except sr.WaitTimeoutError:
            self.brain.logger.debug("¢°¹¼° ¾¶и´°½и µи")
            return None
        except sr.UnknownValueError:
            self.brain.logger.debug("µ ´°»¾ °¿¾·½° µ")
            return None
        except sr.RequestError as e:
            self.brain.logger.error(f"и±º° µви° °¿¾·½°в°½и: {e}")
            return None
        except Exception as e:
            self.brain.logger.error(f"и±º° °¿¾·½°в°½и: {e}")
            return None

    def listen_for_wake_word(self) -> bool:
        """¡»° wake word."""
        text = self.listen()
        if text and self.wake_word.lower() in text.lower():
            return True
        return False

    def continuous_listen(self, callback):
        """µ¿µв½¾µ ¿¾»ив°½иµ."""
        while True:
            text = self.listen()
            if text:
                callback(text)
