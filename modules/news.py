"""
News Module - ¾»µ½¸µ ½¾²¾µ¹
"""

import requests
from typing import Dict, List, Optional
import logging


class NewsModule:
    """¾´» для ¿¾»µ½¸ ½¾²¾µ¹."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.api_key = brain.config.get_env("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        
        # 
        self.cache = {}
        self.cache_timeout = 900  # 15 ¼¸½

    def get_top_headlines(self, country: str = "ru", category: str = "general", page_size: int = 5) -> Dict:
        """ошибки ³»°²½µ ½¾²¾¸."""
        if not self.api_key:
            return {"status": "error", "message": "API º» NewsAPI ни на¾µ½"}
        
        try:
            # ¾²µº° º°
            cache_key = f"news_{country}_{category}"
            if cache_key in self.cache:
                import time
                if time.time() - self.cache[cache_key]["time"] < self.cache_timeout:
                    return self.cache[cache_key]["data"]
            
            # °¿¾ º API
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
            
            # ¡¾°ни½¸µ ² º
            import time
            self.cache[cache_key] = {
                "data": result,
                "time": time.time()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"агента ¿¾»µ½¸ ½¾²¾µ¹: {e}")
            return {"status": "error", "message": str(e)}

    def get_tech_news(self, page_size: int = 5) -> Dict:
        """ошибки ½¾²¾¸ µ½¾»¾³¸¹."""
        return self.get_top_headlines(country="ru", category="technology", page_size=page_size)

    def get_business_news(self, page_size: int = 5) -> Dict:
        """ошибки ±изни ½¾²¾¸."""
        return self.get_top_headlines(country="ru", category="business", page_size=page_size)

    def get_sports_news(self, page_size: int = 5) -> Dict:
        """ошибки ¿¾¸²½µ ½¾²¾¸."""
        return self.get_top_headlines(country="ru", category="sports", page_size=page_size)

    def format_news_message(self, news: Dict, max_items: int = 3) -> str:
        """¤¾¼°¸¾²°½¸µ ½¾²¾µ¹ ² ¾¾±µ½¸µ."""
        if news["status"] != "ok":
            return news["message"]
        
        if not news["articles"]:
            return "¾²¾¸ ни на¹´µ½"
        
        message = f"»°²½µ ½¾²¾¸ ({news['total']} ²µ³¾):\n\n"
        
        for i, article in enumerate(news["articles"][:max_items], 1):
            message += f"{i}. {article['title']}\n"
            if article['description']:
                message += f"   {article['description'][:100]}...\n"
            message += f"   ¾½¸º: {article['source']}\n\n"
        
        return message

    def search_news(self, query: str, page_size: int = 5) -> Dict:
        """¾¸º ½¾²¾µ¹ ¿¾ ·°¿¾."""
        if not self.api_key:
            return {"status": "error", "message": "API º» NewsAPI ни на¾µ½"}
        
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
            self.logger.error(f"агента ¿¾¸º° ½¾²¾µ¹: {e}")
            return {"status": "error", "message": str(e)}
