"""
 °¿¾·½°²°½¸µ µ¸ JARVIS
"""

import speech_recognition as sr
from typing import Optional, Dict


class VoiceListener:
    """ °¿¾·½°²°½¸µ ³¾»¾¾² º¾¼°½´."""

    def __init__(self, brain):
        self.brain = brain
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.wake_word = brain.config.get("voice", {}).get("wake_word", "´¶°²¸")
        
        # °¾¹º° °¿¾·½°²°½¸
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300

    def listen(self) -> Optional[str]:
        """¡»° ¸ °¿¾·½° µ."""
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
            self.brain.logger.debug("¢°¹¼° ¾¶¸´°½¸ µ¸")
            return None
        except sr.UnknownValueError:
            self.brain.logger.debug("µ ´°»¾ °¿¾·½° µ")
            return None
        except sr.RequestError as e:
            self.brain.logger.error(f"¸±º° µ²¸° °¿¾·½°²°½¸: {e}")
            return None
        except Exception as e:
            self.brain.logger.error(f"¸±º° °¿¾·½°²°½¸: {e}")
            return None

    def listen_for_wake_word(self) -> bool:
        """¡»° wake word."""
        text = self.listen()
        if text and self.wake_word.lower() in text.lower():
            return True
        return False

    def continuous_listen(self, callback):
        """µ¿µ²½¾µ ¿¾»¸²°½¸µ."""
        while True:
            text = self.listen()
            if text:
                callback(text)
