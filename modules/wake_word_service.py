"""
Wake Word µ²¸ - ¾½¾²¾µ ¿¾»¸²°½¸µ "¶°²¸"
"""

import threading
import queue
import time
from typing import Dict, Optional, Callable
import logging


class WakeWordService:
    """¡µ²¸ ¾½¾²¾³¾ ¿¾»¸²°½¸ wake word."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.wake_word = brain.config.get("voice.wake_word", "´¶°²¸")
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None

    def start(self, callback: Callable = None) -> Dict:
        """°¿º µ²¸°."""
        if self.running:
            return {"status": "error", "message": "¡µ²¸ ¶µ ·°¿µ½"}
        
        self.callback = callback
        self.running = True
        
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
        self.logger.info(f"Wake word µ²¸ ·°¿µ½. ¡»° '{self.wake_word}'")
        return {"status": "ok", "message": f"¡»° '{self.wake_word}'"}

    def stop(self) -> Dict:
        """°½¾²º° µ²¸°."""
        if not self.running:
            return {"status": "error", "message": "¡µ²¸ ни ·°¿µ½"}
        
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        self.logger.info("Wake word µ²¸ ¾°½¾²»µ½")
        return {"status": "ok", "message": "¡µ²¸ ¾°½¾²»µ½"}

    def _listen_loop(self):
        """¦¸º» ¿¾»¸²°½¸."""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            
            self.logger.info("Wake word: ¼¸º¾¾½ ¸½¸¸°»из¸¾²°½")
            
            while self.running:
                try:
                    with microphone as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=2)
                    
                    #  °¿¾·на²°½¸µ
                    try:
                        text = recognizer.recognize_google(audio, language="ru-RU")
                        text_lower = text.lower().strip()
                        
                        # ¾²µº° wake word
                        if self.wake_word in text_lower:
                            self.logger.info(f"Wake word ¾±на¶µ½: {text}")
                            
                            if self.callback:
                                self.callback(text)
                    
                    except sr.UnknownValueError:
                        pass  # µ °¿¾·на½¾
                    except sr.RequestError as e:
                        self.logger.error(f"агента °¿¾·на²°½¸: {e}")
                
                except Exception as e:
                    # ¢°¹¼° ¸»¸ ´³° ¾¸±º° - ¿¾´¾»¶°µ¼
                    pass
                
                time.sleep(0.1)
        
        except Exception as e:
            self.logger.error(f"агента wake word µ²¸°: {e}")

    def is_running(self) -> bool:
        """¾²µ¸, ·°¿µ½ »¸ µ²¸."""
        return self.running

    def set_wake_word(self, wake_word: str) -> Dict:
        """£°½¾²¸ wake word."""
        self.wake_word = wake_word.lower().strip()
        self.brain.config.set("voice.wake_word", self.wake_word)
        self.logger.info(f"Wake word °½¾²»µ½: {self.wake_word}")
        return {"status": "ok", "message": f"Wake word: {self.wake_word}"}
