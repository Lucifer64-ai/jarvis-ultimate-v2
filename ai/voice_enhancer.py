"""
£»µ½¸µ °¿¾·½°²°½¸ µ¸ JARVIS
"""

import re
from typing import List, Dict


class VoiceEnhancer:
    """£»µ½¸µ º°µ²° °¿¾·½°²°½¸ µ¸."""

    def __init__(self, brain):
        self.brain = brain
        self.corrections = self._load_corrections()

    def _load_corrections(self) -> Dict[str, str]:
        """°³·º° »¾²° ¸¿°²»µ½¸¹."""
        return {
            # §°µ ¾¸±º¸ °¿¾·½°²°½¸
            "´¶°²¸": "´¶°²¸",
            "jarvis": "´¶°²¸",
            "¶°²¸": "´¶°²¸",
            "²¸": "´¶°²¸",
            
            # ¡¸µ¼½µ º¾¼°½´
            "²º»¸": "²º»¸",
            "²º»¸": "²º»¸",
            "¾º¾¹": "¾º¾¹",
            "·°¿¸": "·°¿¸",
            "¿¾º°¶¸": "¿¾º°¶¸",
            
            # ¸»¾¶µ½¸
            "±»¾º½¾": "±»¾º½¾",
            "notepad": "±»¾º½¾",
            "º°»º»¾": "º°»º»¾",
            "±": "youtube",
            "youtube": "youtube",
            "³¸°±": "github",
            "github": "github",
            
            # µ¹²¸
            "²µ¼": "²µ¼",
            "´°°": "´°°",
            "¿¾³¾´°": "¿¾³¾´°",
            "º¾¾": "º¾¾",
            "¸½µ½µ": "¸½µ½µ",
        }

    def enhance(self, text: str) -> str:
        """£»µ½¸µ °¿¾·½°½½¾³¾ µº°."""
        if not text:
            return text
        
        # ¸²µ´µ½¸µ º ½¸¶½µ¼ µ³¸
        text = text.lower().strip()
        
        # £´°»µ½¸µ »¸½¸ ¿¾±µ»¾²
        text = re.sub(r'\s+', ' ', text)
        
        # ¿°²»µ½¸µ ° ¾¸±¾º
        for wrong, correct in self.corrections.items():
            text = text.replace(wrong, correct)
        
        # £´°»µ½¸µ »¾²-¿°°·¸¾²
        parasites = ["¼", "", "½", "¸¿°", "º¾¾µ"]
        for parasite in parasites:
            text = text.replace(parasite, "")
        
        # ¸º° ¾ »¸½¸ ¿¾±µ»¾² ¿¾»µ ´°»µ½¸
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def extract_numbers(self, text: str) -> List[int]:
        """·²»µµ½¸µ ¸µ» ¸· µº°."""
        numbers = re.findall(r'\d+', text)
        return [int(n) for n in numbers]

    def extract_time(self, text: str) -> Dict:
        """·²»µµ½¸µ ²µ¼µ½¸ ¸· µº°."""
        # °µ½ ´» ²µ¼µ½¸ HH:MM
        time_pattern = r'(\d{1,2}):(\d{2})'
        match = re.search(time_pattern, text)
        
        if match:
            return {
                "hour": int(match.group(1)),
                "minute": int(match.group(2))
            }
        
        # °µ½ ´» "µµ· N ¼¸½/°¾²"
        relative_pattern = r'µµ·\s+(\d+)\s+(¼¸½|°|µº½´)'
        match = re.search(relative_pattern, text)
        
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            return {
                "value": value,
                "unit": unit,
                "relative": True
            }
        
        return {}

    def extract_date(self, text: str) -> Dict:
        """·²»µµ½¸µ ´° ¸· µº°."""
        # °µ½ ´» ´° DD.MM.YYYY
        date_pattern = r'(\d{1,2})[.\-\/](\d{1,2})[.\-\/](\d{4})'
        match = re.search(date_pattern, text)
        
        if match:
            return {
                "day": int(match.group(1)),
                "month": int(match.group(2)),
                "year": int(match.group(3))
            }
        
        # ½¾¸µ»½µ ´°
        if "·°²°" in text:
            return {"relative": "tomorrow"}
        elif "²µ°" in text:
            return {"relative": "yesterday"}
        elif "µ³¾´½" in text:
            return {"relative": "today"}
        
        return {}

    def normalize_command(self, text: str) -> str:
        """¾¼°»¸·°¸ º¾¼°½´ ´» ¾±°±¾º¸."""
        text = self.enhance(text)
        
        # £´°»µ½¸µ wake word µ»¸ µ
        wake_words = ["´¶°²¸", "jarvis"]
        for wake in wake_words:
            if text.startswith(wake):
                text = text[len(wake):].strip()
                break
        
        return text
