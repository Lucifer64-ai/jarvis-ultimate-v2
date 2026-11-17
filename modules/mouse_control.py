"""
Модуль управления мышкой JARVIS
Управление курсором мыши, кликами, перетаскиванием и прокруткой экрана.
"""

from typing import Dict, Optional, Tuple
import logging

try:
    import pyautogui
    PY_AUTOGUI_AVAILABLE = True
except ImportError:
    pyautogui = None
    PY_AUTOGUI_AVAILABLE = False


class MouseControl:
    """Модуль для управления мышью и экраном."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        if PY_AUTOGUI_AVAILABLE:
            # Отключаем fail-safe для JARVIS (можно вернуть через settings)
            pyautogui.FAILSAFE = False
            # Задержка между действиями для стабильности
            pyautogui.PAUSE = 0.1

        self.screen_size = self._get_screen_size()

    def _get_screen_size(self) -> Tuple[int, int]:
        """Получение размера экрана."""
        if not PY_AUTOGUI_AVAILABLE:
            return (0, 0)
        try:
            return pyautogui.size()
        except Exception as e:
            self.logger.error(f"Не удалось получить размер экрана: {e}")
            return (0, 0)

    def _check_available(self) -> bool:
        """Проверка доступности pyautogui."""
        if not PY_AUTOGUI_AVAILABLE:
            self.logger.warning("pyautogui не установлен. Установите: pip install pyautogui")
            return False
        return True

    # === ПЕРЕМЕЩЕНИЕ КУРСОРА ===

    def move_to(self, x: int, y: int, duration: float = 0.5) -> Dict:
        """Переместить курсор мыши в координаты (x, y)."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            pyautogui.moveTo(x, y, duration=duration)
            self.logger.info(f"Курсор перемещён в ({x}, {y})")
            return {"status": "ok", "message": f"Курсор в точке ({x}, {y})", "x": x, "y": y}
        except Exception as e:
            self.logger.error(f"Ошибка перемещения курсора: {e}")
            return {"status": "error", "message": str(e)}

    def move_relative(self, dx: int, dy: int, duration: float = 0.5) -> Dict:
        """Переместить курсор относительно текущей позиции."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            pyautogui.moveRel(dx, dy, duration=duration)
            self.logger.info(f"Курсор перемещён на ({dx}, {dy})")
            return {"status": "ok", "message": f"Курсор смещён на ({dx}, {dy})", "dx": dx, "dy": dy}
        except Exception as e:
            self.logger.error(f"Ошибка смещения курсора: {e}")
            return {"status": "error", "message": str(e)}

    def get_position(self) -> Dict:
        """Получить текущие координаты курсора."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            x, y = pyautogui.position()
            return {"status": "ok", "x": x, "y": y, "message": f"Курсор в ({x}, {y})"}
        except Exception as e:
            self.logger.error(f"Ошибка получения позиции: {e}")
            return {"status": "error", "message": str(e)}

    def center_cursor(self) -> Dict:
        """Переместить курсор в центр экрана."""
        w, h = self.screen_size
        if w == 0 or h == 0:
            return {"status": "error", "message": "Неизвестен размер экрана"}
        return self.move_to(w // 2, h // 2)

    # === КЛИКИ ===

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left') -> Dict:
        """Клик мышью в точке (x, y) или в текущей позиции."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            if x is not None and y is not None:
                pyautogui.click(x=x, y=y, button=button)
                self.logger.info(f"Клик {button} в ({x}, {y})")
                return {"status": "ok", "message": f"Клик {button} в ({x}, {y})", "x": x, "y": y, "button": button}
            else:
                pyautogui.click(button=button)
                x, y = pyautogui.position()
                self.logger.info(f"Клик {button} в ({x}, {y})")
                return {"status": "ok", "message": f"Клик {button} в ({x}, {y})", "x": x, "y": y, "button": button}
        except Exception as e:
            self.logger.error(f"Ошибка клика: {e}")
            return {"status": "error", "message": str(e)}

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> Dict:
        """Двойной клик."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            if x is not None and y is not None:
                pyautogui.doubleClick(x=x, y=y)
            else:
                pyautogui.doubleClick()
            x, y = pyautogui.position()
            self.logger.info(f"Двойной клик в ({x}, {y})")
            return {"status": "ok", "message": f"Двойной клик в ({x}, {y})", "x": x, "y": y}
        except Exception as e:
            self.logger.error(f"Ошибка двойного клика: {e}")
            return {"status": "error", "message": str(e)}

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> Dict:
        """Правый клик."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            if x is not None and y is not None:
                pyautogui.rightClick(x=x, y=y)
            else:
                pyautogui.rightClick()
            x, y = pyautogui.position()
            self.logger.info(f"Правый клик в ({x}, {y})")
            return {"status": "ok", "message": f"Правый клик в ({x}, {y})", "x": x, "y": y}
        except Exception as e:
            self.logger.error(f"Ошибка правого клика: {e}")
            return {"status": "error", "message": str(e)}

    def drag_to(self, x: int, y: int, duration: float = 0.5) -> Dict:
        """Перетащить мышь из текущей позиции в (x, y)."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            pyautogui.dragTo(x, y, duration=duration)
            self.logger.info(f"Перетаскивание в ({x}, {y})")
            return {"status": "ok", "message": f"Перетащено в ({x}, {y})", "x": x, "y": y}
        except Exception as e:
            self.logger.error(f"Ошибка перетаскивания: {e}")
            return {"status": "error", "message": str(e)}

    def drag_rel(self, dx: int, dy: int, duration: float = 0.5) -> Dict:
        """Перетащить мышь относительно текущей позиции."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            pyautogui.dragRel(dx, dy, duration=duration)
            self.logger.info(f"Перетаскивание на ({dx}, {dy})")
            return {"status": "ok", "message": f"Перетащено на ({dx}, {dy})", "dx": dx, "dy": dy}
        except Exception as e:
            self.logger.error(f"Ошибка перетаскивания: {e}")
            return {"status": "error", "message": str(e)}

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> Dict:
        """Прокрутка колёсика мыши."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x=x, y=y)
            else:
                pyautogui.scroll(clicks)
            direction = "вверх" if clicks > 0 else "вниз"
            self.logger.info(f"Прокрутка {direction} на {abs(clicks)}")
            return {"status": "ok", "message": f"Прокрутка {direction} на {abs(clicks)}", "clicks": clicks}
        except Exception as e:
            self.logger.error(f"Ошибка прокрутки: {e}")
            return {"status": "error", "message": str(e)}

    def scroll_up(self, clicks: int = 3) -> Dict:
        """Прокрутить вверх."""
        return self.scroll(clicks)

    def scroll_down(self, clicks: int = 3) -> Dict:
        """Прокрутить вниз."""
        return self.scroll(-clicks)

    def press_key(self, key: str) -> Dict:
        """Нажатие клавиши (для сочетаний с мышью)."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            pyautogui.press(key)
            self.logger.info(f"Нажата клавиша: {key}")
            return {"status": "ok", "message": f"Нажата клавиша: {key}", "key": key}
        except Exception as e:
            self.logger.error(f"Ошибка нажатия клавиши: {e}")
            return {"status": "error", "message": str(e)}

    def hotkey(self, *keys) -> Dict:
        """Сочетание клавиш (например, ctrl+c)."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            pyautogui.hotkey(*keys)
            self.logger.info(f"Сочетание клавиш: {'+'.join(keys)}")
            return {"status": "ok", "message": f"Сочетание: {'+'.join(keys)}", "keys": list(keys)}
        except Exception as e:
            self.logger.error(f"Ошибка сочетания клавиш: {e}")
            return {"status": "error", "message": str(e)}

    def type_text(self, text: str, interval: float = 0.01) -> Dict:
        """Набор текста."""
        if not self._check_available():
            return {"status": "error", "message": "pyautogui недоступен"}
        try:
            pyautogui.typewrite(text, interval=interval)
            self.logger.info(f"Введён текст: {text[:50]}...")
            return {"status": "ok", "message": f"Введён текст ({len(text)} символов)", "length": len(text)}
        except Exception as e:
            self.logger.error(f"Ошибка ввода текста: {e}")
            return {"status": "error", "message": str(e)}

    def get_screen_size(self) -> Dict:
        """Получить размер экрана."""
        w, h = self.screen_size
        return {
            "status": "ok",
            "width": w,
            "height": h,
            "message": f"Размер экрана: {w}x{h}"
        }

    def get_info(self) -> Dict:
        """Полная информация о модуле."""
        x, y = pyautogui.position() if PY_AUTOGUI_AVAILABLE else (0, 0)
        w, h = self.screen_size
        return {
            "status": "ok",
            "available": PY_AUTOGUI_AVAILABLE,
            "cursor": {"x": x, "y": y},
            "screen": {"width": w, "height": h},
            "message": "Модуль управления мышкой готов"
        }
