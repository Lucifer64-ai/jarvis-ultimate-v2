"""
JARVIS Pixel Eyes Module
GUI автоматизация для приложений без API
"""

import numpy as np
from PIL import Image, ImageGrab
import pytesseract
from typing import List, Dict, Tuple, Optional

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

class PixelEyes:
    """Модуль для работы с GUI через компьютерное зрение"""

    def __init__(self):
        self.confidence_threshold = 0.8
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def _check_pyautogui(self):
        """Проверить доступность pyautogui."""
        if pyautogui is None:
            raise ImportError("pyautogui недоступен. Установите: pip install pyautogui")

    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Захват экрана в формате OpenCV"""
        if cv2 is None:
            raise ImportError("OpenCV (cv2) недоступен. Установите: pip install opencv-python")

        if region:
            screenshot = ImageGrab.grab(bbox=region)
        else:
            screenshot = ImageGrab.grab()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def find_text_on_screen(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict]:
        """Поиск текста на экране с помощью OCR"""
        screenshot = self.capture_screen(region)
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

        found_elements = []
        n_boxes = len(data['text'])

        for i in range(n_boxes):
            text = data['text'][i].strip()
            if text and target_text.lower() in text.lower():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                confidence = int(data['conf'][i]) / 100.0

                if confidence >= self.confidence_threshold:
                    found_elements.append({
                        'text': text,
                        'x': x + w // 2,
                        'y': y + h // 2,
                        'width': w,
                        'height': h,
                        'confidence': confidence
                    })

        return found_elements

    def click_on_text(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Клик по найденному тексту"""
        self._check_pyautogui()
        elements = self.find_text_on_screen(target_text, region)
        if elements:
            best = max(elements, key=lambda x: x['confidence'])
            pyautogui.click(best['x'], best['y'])
            return True
        return False

    def number_elements(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[int, Dict]:
        """Нумерация всех интерактивных элементов на экране"""
        screenshot = self.capture_screen(region)
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

        numbered_elements = {}
        element_num = 1

        n_boxes = len(data['text'])
        for i in range(n_boxes):
            text = data['text'][i].strip()
            if text and len(text) > 1:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                confidence = int(data['conf'][i]) / 100.0

                if confidence >= 0.6:
                    numbered_elements[element_num] = {
                        'text': text,
                        'x': x + w // 2,
                        'y': y + h // 2,
                        'width': w,
                        'height': h,
                        'type': 'text',
                        'confidence': confidence
                    }
                    element_num += 1

        return numbered_elements

    def click_by_number(self, element_number: int, numbered_elements: Dict[int, Dict]) -> bool:
        """Клик по элементу с указанным номером"""
        self._check_pyautogui()
        if element_number in numbered_elements:
            elem = numbered_elements[element_number]
            pyautogui.click(elem['x'], elem['y'])
            return True
        return False
