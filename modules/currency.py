"""
Currency Module - Получение курсов валют
"""

import requests
from typing import Dict, Optional
import logging


class CurrencyModule:
    """Модуль для получения курсов валют."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.base_url = "https://api.exchangerate-api.com/v4/latest"

        # Кэш
        self.cache = {}
        self.cache_timeout = 3600  # 1 час

    def get_rate(self, from_currency: str = "USD", to_currency: str = "RUB") -> Dict:
        """Получить курс валюты."""
        try:
            # Проверка кэша
            cache_key = f"rate_{from_currency}_{to_currency}"
            if cache_key in self.cache:
                import time
                if time.time() - self.cache[cache_key]["time"] < self.cache_timeout:
                    return self.cache[cache_key]["data"]

            # Запрос к API
            url = f"{self.base_url}/{from_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if to_currency not in data["rates"]:
                return {"status": "error", "message": f"Валюта {to_currency} не найдена"}

            rate = data["rates"][to_currency]

            result = {
                "status": "ok",
                "from": from_currency,
                "to": to_currency,
                "rate": round(rate, 2),
                "date": data["date"]
            }

            # Сохранение в кэш
            import time
            self.cache[cache_key] = {
                "data": result,
                "time": time.time()
            }

            return result

        except Exception as e:
            self.logger.error(f"Ошибка получения курса: {e}")
            return {"status": "error", "message": str(e)}

    def get_usd_rub(self) -> Dict:
        """Получить курс USD к RUB."""
        return self.get_rate("USD", "RUB")

    def get_eur_rub(self) -> Dict:
        """Получить курс EUR к RUB."""
        return self.get_rate("EUR", "RUB")

    def get_btc_usd(self) -> Dict:
        """Получить курс Bitcoin к USD."""
        try:
            url = "https://api.coindesk.com/v1/bpi/currentprice/USD.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            rate = data["bpi"]["USD"]["rate_float"]

            return {
                "status": "ok",
                "from": "BTC",
                "to": "USD",
                "rate": round(rate, 2)
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения курса BTC: {e}")
            return {"status": "error", "message": str(e)}

    def format_rate_message(self, rate: Dict) -> str:
        """Форматирование курса в сообщение."""
        if rate["status"] != "ok":
            return rate["message"]

        return f"Курс {rate['from']} к {rate['to']}: {rate['rate']}"

    def get_multiple_rates(self) -> Dict:
        """Получить несколько основных курсов валют."""
        usd_rub = self.get_usd_rub()
        eur_rub = self.get_eur_rub()
        btc_usd = self.get_btc_usd()

        return {
            "status": "ok",
            "usd_rub": usd_rub.get("rate") if usd_rub["status"] == "ok" else None,
            "eur_rub": eur_rub.get("rate") if eur_rub["status"] == "ok" else None,
            "btc_usd": btc_usd.get("rate") if btc_usd["status"] == "ok" else None
        }

    def format_multiple_rates_message(self, rates: Dict) -> str:
        """Форматирование нескольких курсов."""
        if rates["status"] != "ok":
            return "Не удалось получить курсы валют"

        message = "Курсы валют:\n"
        if rates["usd_rub"]:
            message += f"USD/RUB: {rates['usd_rub']}\n"
        if rates["eur_rub"]:
            message += f"EUR/RUB: {rates['eur_rub']}\n"
        if rates["btc_usd"]:
            message += f"BTC/USD: ${rates['btc_usd']}"

        return message
