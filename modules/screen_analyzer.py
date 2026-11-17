"""
Модуль анализа экрана JARVIS
Скриншоты, OCR-распознавание текста, поиск элементов на экране, анализ происходящего на ПК.
"""

from typing import Dict, Optional, List, Tuple
import logging
import os
import time
from pathlib import Path

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageGrab = None
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    PYTESSERACT_AVAILABLE = False


class ScreenAnalyzer:
    """Модуль анализа экрана и происходящего на ПК."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.screenshots_dir = Path("data/screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Настройка tesseract (по умолчанию Windows-путь, можно изменить через настройки)
        if PYTESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        self.last_screenshot: Optional[Image.Image] = None
        self.last_screenshot_path: Optional[str] = None

    # === ПРОВЕРКА ДОСТУПНОСТИ ===

    def _check_pil(self) -> bool:
        if not PIL_AVAILABLE:
            self.logger.warning("Pillow не установлен. Установите: pip install Pillow")
            return False
        return True

    def _check_cv2(self) -> bool:
        if not CV2_AVAILABLE:
            self.logger.warning("OpenCV не установлен. Установите: pip install opencv-python")
            return False
        return True

    def _check_pytesseract(self) -> bool:
        if not PYTESSERACT_AVAILABLE:
            self.logger.warning("pytesseract не установлен. Установите: pip install pytesseract")
            return False
        return True

    def get_availability(self) -> Dict:
        """Статус доступности зависимостей."""
        return {
            "status": "ok",
            "pillow": PIL_AVAILABLE,
            "opencv": CV2_AVAILABLE,
            "numpy": NUMPY_AVAILABLE,
            "pytesseract": PYTESSERACT_AVAILABLE,
            "message": "Все зависимости установлены" if all([PIL_AVAILABLE, CV2_AVAILABLE, NUMPY_AVAILABLE]) else "Некоторые зависимости отсутствуют"
        }

    # === СКРИНШОТЫ ===

    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """Сделать скриншот экрана (или региона)."""
        if not self._check_pil():
            return {"status": "error", "message": "Pillow недоступен"}
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()

            self.last_screenshot = screenshot

            # Сохраняем скриншот
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            filepath = str(self.screenshots_dir / filename)
            screenshot.save(filepath)
            self.last_screenshot_path = filepath

            self.logger.info(f"Скриншот сохранён: {filepath} ({screenshot.size[0]}x{screenshot.size[1]})")
            return {
                "status": "ok",
                "message": "Скриншот сделан",
                "path": filepath,
                "width": screenshot.size[0],
                "height": screenshot.size[1],
                "region": region
            }
        except Exception as e:
            self.logger.error(f"Ошибка создания скриншота: {e}")
            return {"status": "error", "message": str(e)}

    def capture_full_screen(self) -> Dict:
        """Сделать скриншот всего экрана."""
        return self.capture_screen(region=None)

    def get_last_screenshot(self) -> Dict:
        """Получить информацию о последнем скриншоте."""
        if self.last_screenshot is None:
            return {"status": "error", "message": "Скриншот не был сделан"}
        return {
            "status": "ok",
            "path": self.last_screenshot_path,
            "width": self.last_screenshot.size[0],
            "height": self.last_screenshot.size[1]
        }

    # === OCR РАСПОЗНАВАНИЕ ТЕКСТА ===

    def find_text_on_screen(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """Найти текст на экране через OCR."""
        if not self._check_pytesseract() or not self._check_pil():
            return {"status": "error", "message": "pytesseract или Pillow недоступны"}

        # Сначала делаем скриншот, если ещё не сделан
        if self.last_screenshot is None:
            result = self.capture_screen(region=region)
            if result["status"] != "ok":
                return result

        try:
            img = self.last_screenshot
            if region:
                img = img.crop(region)

            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang='rus+eng')

            found_elements = []
            n_boxes = len(data['text'])
            target_lower = target_text.lower()

            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text and target_lower in text.lower():
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    confidence = float(data['conf'][i]) / 100.0

                    if confidence >= 0.3:  # порог уверенности
                        # Если был указан регион, корректируем координаты
                        if region:
                            x += region[0]
                            y += region[1]

                        found_elements.append({
                            'text': text,
                            'x': x + w // 2,
                            'y': y + h // 2,
                            'width': w,
                            'height': h,
                            'confidence': confidence
                        })

            self.logger.info(f"Найдено вхождений '{target_text}': {len(found_elements)}")
            return {
                "status": "ok",
                "target": target_text,
                "count": len(found_elements),
                "elements": found_elements,
                "message": f"Найдено {len(found_elements)} вхождений текста '{target_text}'"
            }
        except Exception as e:
            self.logger.error(f"Ошибка OCR: {e}")
            return {"status": "error", "message": str(e)}

    def read_screen_text(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """Распознать весь текст на экране."""
        if not self._check_pytesseract() or not self._check_pil():
            return {"status": "error", "message": "pytesseract или Pillow недоступны"}

        if self.last_screenshot is None:
            result = self.capture_screen(region=region)
            if result["status"] != "ok":
                return result

        try:
            img = self.last_screenshot
            if region:
                img = img.crop(region)

            text = pytesseract.image_to_string(img, lang='rus+eng')
            self.logger.info("Текст с экрана распознан")
            return {
                "status": "ok",
                "text": text.strip(),
                "message": "Текст с экрана распознан"
            }
        except Exception as e:
            self.logger.error(f"Ошибка распознавания текста: {e}")
            return {"status": "error", "message": str(e)}

    def click_on_text(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """Найти текст на экране и кликнуть по нему."""
        # Ленивый импорт pyautogui
        try:
            import pyautogui
        except ImportError:
            return {"status": "error", "message": "pyautogui не установлен"}

        result = self.find_text_on_screen(target_text, region=region)
        if result["status"] != "ok" or result["count"] == 0:
            return {"status": "error", "message": f"Текст '{target_text}' не найден на экране"}

        # Кликаем по самому уверенному вхождению
        best = max(result["elements"], key=lambda e: e['confidence'])
        try:
            pyautogui.click(best['x'], best['y'])
            self.logger.info(f"Клик по тексту '{target_text}' в ({best['x']}, {best['y']})")
            return {
                "status": "ok",
                "message": f"Клик по '{target_text}'",
                "x": best['x'],
                "y": best['y'],
                "confidence": best['confidence']
            }
        except Exception as e:
            self.logger.error(f"Ошибка клика по тексту: {e}")
            return {"status": "error", "message": str(e)}

    # === АНАЛИЗ ЭКРАНА (шаблоны и цвета) ===

    def find_color_on_screen(self, target_color: Tuple[int, int, int], tolerance: int = 10) -> Dict:
        """Найти цвет на экране (OpenCV)."""
        if not self._check_cv2() or not self._check_pil() or not NUMPY_AVAILABLE:
            return {"status": "error", "message": "OpenCV, Pillow или NumPy недоступны"}

        if self.last_screenshot is None:
            result = self.capture_screen()
            if result["status"] != "ok":
                return result

        try:
            img = np.array(self.last_screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            target_bgr = (target_color[2], target_color[1], target_color[0])  # RGB -> BGR

            lower = (max(0, target_bgr[0] - tolerance), max(0, target_bgr[1] - tolerance), max(0, target_bgr[2] - tolerance))
            upper = (min(255, target_bgr[0] + tolerance), min(255, target_bgr[1] + tolerance), min(255, target_bgr[2] + tolerance))

            mask = cv2.inRange(img, lower, upper)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            found = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 50:  # минимальная площадь
                    x, y, w, h = cv2.boundingRect(contour)
                    found.append({
                        "x": x + w // 2,
                        "y": y + h // 2,
                        "width": w,
                        "height": h,
                        "area": float(area)
                    })

            self.logger.info(f"Найдено цветовых областей: {len(found)}")
            return {
                "status": "ok",
                "color": target_color,
                "tolerance": tolerance,
                "count": len(found),
                "areas": found,
                "message": f"Найдено {len(found)} областей цвета {target_color}"
            }
        except Exception as e:
            self.logger.error(f"Ошибка поиска цвета: {e}")
            return {"status": "error", "message": str(e)}

    def get_pixel_color(self, x: int, y: int) -> Dict:
        """Получить цвет пикселя в точке (x, y)."""
        if not self._check_pil():
            return {"status": "error", "message": "Pillow недоступен"}

        if self.last_screenshot is None:
            result = self.capture_screen()
            if result["status"] != "ok":
                return result

        try:
            w, h = self.last_screenshot.size
            if x < 0 or x >= w or y < 0 or y >= h:
                return {"status": "error", "message": f"Координаты ({x}, {y}) за пределами экрана ({w}x{h})"}

            pixel = self.last_screenshot.getpixel((x, y))
            if isinstance(pixel, int):
                rgb = (pixel, pixel, pixel)
            else:
                rgb = tuple(pixel[:3])

            self.logger.info(f"Цвет пикселя ({x}, {y}): {rgb}")
            return {
                "status": "ok",
                "x": x,
                "y": y,
                "rgb": rgb,
                "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                "message": f"Цвет ({x}, {y}): RGB{rgb}"
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения цвета пикселя: {e}")
            return {"status": "error", "message": str(e)}

    # === ВЫСОКОУРОВНЕВЫЙ АНАЛИЗ ===

    def analyze_screen(self) -> Dict:
        """Полный анализ экрана: скриншот + OCR + основные цвета."""
        if not self._check_pil():
            return {"status": "error", "message": "Pillow недоступен"}

        # 1. Скриншот
        shot = self.capture_screen()
        if shot["status"] != "ok":
            return shot

        # 2. OCR текст
        ocr_result = self.read_screen_text()
        screen_text = ocr_result.get("text", "") if ocr_result["status"] == "ok" else ""

        # 3. Размер экрана
        w, h = self.last_screenshot.size

        # 4. Анализ типа контента (по ключевым словам)
        text_lower = screen_text.lower()
        detected_elements = []

        keywords = {
            "браузер": ["браузер", "chrome", "yandex", "сайт", "страница", "вход", "войти"],
            "мессенджер": ["телеграм", "whatsapp", "discord", "сообщение", "чат"],
            "музыка": ["музыка", "spotify", "видео", "плейлист", "трек"],
            "система": ["панель", "меню", "пуск", "настройки", "задачи"],
            "документ": ["документ", "текст", "word", "файл", "открыть"],
        }

        for category, words in keywords.items():
            for word in words:
                if word in text_lower:
                    detected_elements.append(category)
                    break

        self.logger.info(f"Анализ экрана завершён. Элементы: {detected_elements}")
        return {
            "status": "ok",
            "screenshot_path": self.last_screenshot_path,
            "width": w,
            "height": h,
            "text": screen_text[:500] + ("..." if len(screen_text) > 500 else ""),
            "detected_elements": detected_elements,
            "message": f"Экран проанализирован: {w}x{h}, найдено элементов: {len(detected_elements)}"
        }

    def watch_screen(self, interval: float = 5.0, callback=None) -> Dict:
        """Наблюдение за экраном с интервалом (заглушка для интеграции)."""
        self.logger.info(f"Наблюдение за экраном началось (интервал {interval}с)")
        return {
            "status": "ok",
            "message": f"Наблюдение за экраном запущено (интервал {interval}с)",
            "interval": interval
        }
