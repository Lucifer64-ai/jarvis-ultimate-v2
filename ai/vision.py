"""
JARVIS Vision Module
Анализ скриншотов и изображений через GPT-4V
"""

import base64
import io
from PIL import Image, ImageGrab
import requests
import json
from typing import Optional, Dict, Any

class VisionModule:
    """Модуль компьютерного зрения для JARVIS"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def capture_screen(self, region: Optional[tuple] = None) -> Image.Image:
        """Захват скриншота экрана"""
        if region:
            return ImageGrab.grab(bbox=region)
        return ImageGrab.grab()

    def encode_image(self, image: Image.Image) -> str:
        """Кодирование изображения в base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def analyze_screen(self, question: str, image: Optional[Image.Image] = None) -> str:
        """Анализ скриншота с вопросом"""
        if image is None:
            image = self.capture_screen()

        base64_image = self.encode_image(image)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        result = response.json()

        return result['choices'][0]['message']['content']

    def describe_screen(self) -> str:
        """Описание текущего состояния экрана"""
        return self.analyze_screen("Опиши подробно, что ты видишь на этом экране.")

    def find_element(self, element_description: str) -> Dict[str, Any]:
        """Поиск элемента на экране"""
        question = f"""
        Найди на экране элемент: {element_description}
        Верни JSON с полями: found, x, y, width, height, confidence
        """

        response = self.analyze_screen(question)

        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(response[start:end])
        except:
            pass

        return {"found": False, "confidence": 0}

    def read_text(self, region: Optional[tuple] = None) -> str:
        """Чтение текста с экрана (OCR через Vision)"""
        image = self.capture_screen(region) if region else self.capture_screen()
        return self.analyze_screen("Прочитай весь текст на этом изображении.", image)
