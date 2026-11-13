"""
Weather Module - ¾»µ½иµ и½¾¼°ии ¾ ¿¾³¾´µ
"""

import requests
from typing import Dict, Optional
import logging


class WeatherModule:
    """¾´» ´» ¿¾»µ½и ¿¾³¾´."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.api_key = brain.config.get_env("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        #  ´»¥¥° ·°¿¾¾в
        self.cache = {}
        self.cache_timeout = 600  # 10 ¼и½

    def get_weather(self, city: str = "¾ºв°") -> Dict:
        """¾»и µº ¿¾³¾´."""
        if not self.api_key:
            return {"status": "error", "message": "API º» OpenWeather ½µ ½°¾µ½"}
        
        try:
            # ¾вµº° º°
            cache_key = f"weather_{city}"
            if cache_key in self.cache:
                import time
                if time.time() - self.cache[cache_key]["time"] < self.cache_timeout:
                    return self.cache[cache_key]["data"]
            
            # °¿¾ º API
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
            
            # ¤¾¼°и¾в°½иµ ¾вµ°
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
            
            # ¡¾°½µ½иµ в º
            import time
            self.cache[cache_key] = {
                "data": weather_info,
                "time": time.time()
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"и±º° ¿¾»µ½и ¿¾³¾´: {e}")
            return {"status": "error", "message": f"µ ´°»¾ ¿¾»и ¿¾³¾´: {e}"}
        except Exception as e:
            self.logger.error(f"и±º° ¾±°±¾ºи ¿¾³¾´: {e}")
            return {"status": "error", "message": str(e)}

    def get_forecast(self, city: str = "¾ºв°", days: int = 5) -> Dict:
        """¾»и ¿¾³½¾· ¿¾³¾´."""
        if not self.api_key:
            return {"status": "error", "message": "API º» OpenWeather ½µ ½°¾µ½"}
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "ru",
                "cnt": days * 8  # 8 и½µв°»¾в в ´µ½ (º°¶´µ 3 °°)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # ¿¿и¾вº° ¿¾ ´½¼
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
            self.logger.error(f"и±º° ¿¾»µ½и ¿¾³½¾·°: {e}")
            return {"status": "error", "message": str(e)}

    def format_weather_message(self, weather: Dict) -> str:
        """¤¾¼°и¾в°½иµ ¿¾³¾´ в ¾¾±µ½иµ."""
        if weather["status"] != "ok":
            return weather["message"]
        
        return (
            f" ³¾¾´µ {weather['city']} µ¹° {weather['temperature']}°C, "
            f"{weather['description']}. "
            f"°µ º°º {weather['feels_like']}°C. "
            f"»°¶½¾ {weather['humidity']}%, вµµ {weather['wind_speed']} ¼/."
        )

    def format_forecast_message(self, forecast: Dict) -> str:
        """¤¾¼°и¾в°½иµ ¿¾³½¾·° в ¾¾±µ½иµ."""
        if forecast["status"] != "ok":
            return forecast["message"]
        
        message = f"¾³½¾· ´» {forecast['city']}:\n"
        for day in forecast["forecast"]:
            message += f"{day['date']}: ¾ {day['temp_min']}°C ´¾ {day['temp_max']}°C, {day['description']}\n"
        
        return message
