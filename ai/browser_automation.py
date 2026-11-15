"""
JARVIS Browser Automation Module
Автоматизация браузера через Playwright
"""

import time
from typing import Optional, List, Dict

try:
    from playwright.sync_api import sync_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    sync_playwright = None
    Page = None
    Browser = None
    PLAYWRIGHT_AVAILABLE = False

class BrowserAutomation:
    """Модуль автоматизации браузера"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

        if not PLAYWRIGHT_AVAILABLE:
            print("⚠️ playwright не установлен. Установите: pip install playwright && playwright install")

    def start(self):
        """Запуск браузера"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("playwright недоступен")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        print("🌐 Браузер запущен")

    def stop(self):
        """Остановка браузера"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("🔴 Браузер остановлен")

    def navigate(self, url: str):
        """Переход по URL"""
        if not self.page:
            self.start()
        self.page.goto(url)
        print(f"📄 Открыт: {url}")

    def find_tab(self, title: str) -> bool:
        """Поиск вкладки по заголовку"""
        if not self.browser:
            return False

        for context in self.browser.contexts:
            for page in context.pages:
                if title.lower() in page.title().lower():
                    page.bring_to_front()
                    self.page = page
                    print(f"✅ Найдена вкладка: {page.title()}")
                    return True

        print(f"❌ Вкладка не найдена: {title}")
        return False

    def click_element(self, selector: str):
        """Клик по элементу"""
        if not self.page:
            return False

        try:
            self.page.click(selector)
            print(f"✅ Клик: {selector}")
            return True
        except Exception as e:
            print(f"❌ Ошибка клика: {e}")
            return False

    def fill_form(self, selector: str, value: str):
        """Заполнение поля формы"""
        if not self.page:
            return False

        try:
            self.page.fill(selector, value)
            print(f"✅ Заполнено: {selector} = {value}")
            return True
        except Exception as e:
            print(f"❌ Ошибка заполнения: {e}")
            return False

    def pause_video(self):
        """Пауза видео на странице"""
        if not self.page:
            return False

        try:
            self.page.evaluate("document.querySelector('video')?.pause()")
            print("⏸️ Видео поставлено на паузу")
            return True
        except Exception as e:
            print(f"❌ Ошибка паузы видео: {e}")
            return False

    def play_video(self):
        """Воспроизведение видео"""
        if not self.page:
            return False

        try:
            self.page.evaluate("document.querySelector('video')?.play()")
            print("▶️ Видео воспроизводится")
            return True
        except Exception as e:
            print(f"❌ Ошибка воспроизведения: {e}")
            return False

    def get_page_content(self) -> str:
        """Получение текстового содержимого страницы"""
        if not self.page:
            return ""
        return self.page.inner_text("body")

    def execute_javascript(self, script: str):
        """Выполнение JavaScript"""
        if not self.page:
            return None

        try:
            result = self.page.evaluate(script)
            print(f"✅ JS выполнен")
            return result
        except Exception as e:
            print(f"❌ Ошибка JS: {e}")
            return None

    def take_screenshot(self, path: str = "screenshot.png"):
        """Скриншот страницы"""
        if not self.page:
            return False

        try:
            self.page.screenshot(path=path)
            print(f"📸 Скриншот сохранён: {path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка скриншота: {e}")
            return False

    def search_google(self, query: str):
        """Поиск в Google"""
        self.navigate("https://www.google.com")
        self.fill_form('textarea[name="q"]', query)
        self.page.press('textarea[name="q"]', 'Enter')
        self.page.wait_for_load_state("networkidle")
        print(f"🔍 Поиск: {query}")
