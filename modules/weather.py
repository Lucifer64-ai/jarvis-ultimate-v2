"""
Weather Module - Получение текущей погоды и прогноза
"""

import requests
from typing import Dict, Optional
import logging


class WeatherModule:
    """Модуль для получения текущей погоды и прогноза."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.api_key = brain.config.get_env("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"

        # Простой кэш для запросов
        self.cache = {}
        self.cache_timeout = 600  # 10 минут

    def get_weather(self, city: str = "Москва") -> Dict:
        """Получить текущую погоду."""
        if not self.api_key:
            return {"status": "error", "message": "API ключ OpenWeather не настроен"}

        try:
            # Проверка кэша
            cache_key = f"weather_{city}"
            if cache_key in self.cache:
                import time
                if time.time() - self.cache[cache_key]["time"] < self.cache_timeout:
                    return self.cache[cache_key]["data"]

            # Запрос к API
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "ru"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Формирование ответа
            weather_info = {
                "status": "ok",
                "city": city,
                "temperature": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "pressure": data["main"]["pressure"]
            }

            # Сохранение в кэш
            import time
            self.cache[cache_key] = {
                "data": weather_info,
                "time": time.time()
            }

            return weather_info

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка получения погоды: {e}")
            return {"status": "error", "message": f"Не удалось получить погоду: {e}"}
        except Exception as e:
            self.logger.error(f"Ошибка обработки погоды: {e}")
            return {"status": "error", "message": str(e)}

    def get_forecast(self, city: str = "Москва", days: int = 5) -> Dict:
        """Получить прогноз погоды."""
        if not self.api_key:
            return {"status": "error", "message": "API ключ OpenWeather не настроен"}

        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "ru",
                "cnt": days * 8  # 8 интервалов в дне (каждые 3 часа)
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Группировка по дням
            forecast = []
            for i in range(0, len(data["list"]), 8):
                day_data = data["list"][i:i+8]
                if day_data:
                    temps = [d["main"]["temp"] for d in day_data]
                    forecast.append({
                        "date": day_data[0]["dt_txt"].split()[0],
                        "temp_min": round(min(temps)),
                        "temp_max": round(max(temps)),
                        "description": day_data[4]["weather"]["description"] if len(day_data) > 4 else day_data[0]["weather"]["description"]
                    })

            return {
                "status": "ok",
                "city": city,
                "forecast": forecast[:days]
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения прогноза: {e}")
            return {"status": "error", "message": str(e)}

    def format_weather_message(self, weather: Dict) -> str:
        """Форматирование погоды в сообщение."""
        if weather["status"] != "ok":
            return weather["message"]

        return (
            f"В городе {weather['city']} сейчас {weather['temperature']}°C, "
            f"{weather['description']}. "
            f"Ощущается как {weather['feels_like']}°C. "
            f"Влажность {weather['humidity']}%, ветер {weather['wind_speed']} м/с."
        )

    def format_forecast_message(self, forecast: Dict) -> str:
        """Форматирование прогноза в сообщение."""
        if forecast["status"] != "ok":
            return forecast["message"]

        message = f"Прогноз для {forecast['city']}:\n"
        for day in forecast["forecast"]:
            message += f"{day['date']}: от {day['temp_min']}°C до {day['temp_max']}°C, {day['description']}\n"

        return message
