"""
News Module - Получение новостей
"""

import requests
from typing import Dict, List, Optional
import logging


class NewsModule:
    """Модуль для получения новостей."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.api_key = brain.config.get_env("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"

        # Кэш
        self.cache = {}
        self.cache_timeout = 900  # 15 минут

    def get_top_headlines(self, country: str = "ru", category: str = "general", page_size: int = 5) -> Dict:
        """Получить главные новости."""
        if not self.api_key:
            return {"status": "error", "message": "API ключ NewsAPI не настроен"}

        try:
            # Проверка кэша
            cache_key = f"news_{country}_{category}"
            if cache_key in self.cache:
                import time
                if time.time() - self.cache[cache_key]["time"] < self.cache_timeout:
                    return self.cache[cache_key]["data"]

            # Запрос к API
            url = f"{self.base_url}/top-headlines"
            params = {
                "country": country,
                "category": category,
                "pageSize": page_size,
                "apiKey": self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", "")
                })

            result = {
                "status": "ok",
                "total": data.get("totalResults", 0),
                "articles": articles
            }

            # Сохранение в кэш
            import time
            self.cache[cache_key] = {
                "data": result,
                "time": time.time()
            }

            return result

        except Exception as e:
            self.logger.error(f"Ошибка получения новостей: {e}")
            return {"status": "error", "message": str(e)}

    def get_tech_news(self, page_size: int = 5) -> Dict:
        """Получить новости технологий."""
        return self.get_top_headlines(country="ru", category="technology", page_size=page_size)

    def get_business_news(self, page_size: int = 5) -> Dict:
        """Получить бизнес новости."""
        return self.get_top_headlines(country="ru", category="business", page_size=page_size)

    def get_sports_news(self, page_size: int = 5) -> Dict:
        """Получить спортивные новости."""
        return self.get_top_headlines(country="ru", category="sports", page_size=page_size)

    def format_news_message(self, news: Dict, max_items: int = 3) -> str:
        """Форматирование новостей в сообщение."""
        if news["status"] != "ok":
            return news["message"]

        if not news["articles"]:
            return "Новости не найдены"

        message = f"Главные новости ({news['total']} всего):\n\n"

        for i, article in enumerate(news["articles"][:max_items], 1):
            message += f"{i}. {article['title']}\n"
            if article['description']:
                message += f"   {article['description'][:100]}...\n"
            message += f"   Источник: {article['source']}\n\n"

        return message

    def search_news(self, query: str, page_size: int = 5) -> Dict:
        """Поиск новостей по запросу."""
        if not self.api_key:
            return {"status": "error", "message": "API ключ NewsAPI не настроен"}

        try:
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "pageSize": page_size,
                "sortBy": "publishedAt",
                "apiKey": self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "url": article.get("url", "")
                })

            return {
                "status": "ok",
                "total": data.get("totalResults", 0),
                "articles": articles
            }

        except Exception as e:
            self.logger.error(f"Ошибка поиска новостей: {e}")
            return {"status": "error", "message": str(e)}
