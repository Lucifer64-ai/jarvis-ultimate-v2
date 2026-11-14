"""
Интеграция JARVIS с Home Assistant
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
import json
import logging


class HomeAssistantIntegration:
    """Управление умным домом через Home Assistant."""

    def __init__(self, brain):
        self.brain = brain

        # Чтение из переменных окружения
        self.url = brain.config.home_assistant_url
        self.token = brain.config.home_assistant_token

        if self.url and self.token:
            self.brain.logger.info(f"Home Assistant подключен: {self.url}")
        else:
            self.brain.logger.warning("Home Assistant не настроен. Добавьте HOME_ASSISTANT_URL и HOME_ASSISTANT_TOKEN в .env")

        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        """Создание HTTP сессии."""
        if not self.url or not self.token:
            raise Exception("Home Assistant не настроен")

        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
            )

    async def close(self):
        """Закрытие сессии."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_states(self) -> Dict:
        """Получить все состояния устройств."""
        await self._ensure_session()
        try:
            async with self.session.get(f"{self.url}/api/states") as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"Status {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

    async def get_entity(self, entity_id: str) -> Dict:
        """Получить состояние конкретного устройства."""
        await self._ensure_session()
        try:
            async with self.session.get(f"{self.url}/api/states/{entity_id}") as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"Status {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

    async def call_service(self, domain: str, service: str, entity_id: str = None, **kwargs) -> Dict:
        """Вызов сервиса Home Assistant."""
        await self._ensure_session()

        data = kwargs.copy()
        if entity_id:
            data["entity_id"] = entity_id

        try:
            async with self.session.post(
                f"{self.url}/api/services/{domain}/{service}",
                json=data
            ) as resp:
                if resp.status == 200:
                    return {"status": "ok"}
                return {"error": f"Status {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

    # === Управление освещением ===

    async def turn_on_light(self, entity_id: str, brightness: int = None, color: tuple = None):
        """Включить свет."""
        kwargs = {}
        if brightness:
            kwargs["brightness"] = int(brightness * 2.55)
        if color:
            kwargs["rgb_color"] = color

        return await self.call_service("light", "turn_on", entity_id, **kwargs)

    async def turn_off_light(self, entity_id: str):
        """Выключить свет."""
        return await self.call_service("light", "turn_off", entity_id)

    async def set_brightness(self, entity_id: str, brightness: int):
        """Установить яркость."""
        return await self.turn_on_light(entity_id, brightness=brightness)

    async def set_color(self, entity_id: str, r: int, g: int, b: int):
        """Установить цвет."""
        return await self.turn_on_light(entity_id, color=(r, g, b))

    # === Управление климатом ===

    async def set_temperature(self, entity_id: str, temperature: float):
        """Установить температуру."""
        return await self.call_service(
            "climate", "set_temperature",
            entity_id, temperature=temperature
        )

    async def set_hvac_mode(self, entity_id: str, mode: str):
        """Установить режим HVAC."""
        return await self.call_service(
            "climate", "set_hvac_mode",
            entity_id, hvac_mode=mode
        )

    # === Управление медиа ===

    async def media_play(self, entity_id: str):
        """Воспроизвести медиа."""
        return await self.call_service("media_player", "media_play", entity_id)

    async def media_pause(self, entity_id: str):
        """Пауза медиа."""
        return await self.call_service("media_player", "media_pause", entity_id)

    async def media_stop(self, entity_id: str):
        """Остановить медиа."""
        return await self.call_service("media_player", "media_stop", entity_id)

    async def set_volume(self, entity_id: str, volume: float):
        """Установить громкость."""
        return await self.call_service(
            "media_player", "volume_set",
            entity_id, volume_level=volume
        )

    # === Управление замками ===

    async def lock(self, entity_id: str):
        """Заблокировать замок."""
        return await self.call_service("lock", "lock", entity_id)

    async def unlock(self, entity_id: str):
        """Разблокировать замок."""
        return await self.call_service("lock", "unlock", entity_id)

    # === Сцены и скрипты ===

    async def activate_scene(self, entity_id: str):
        """Активировать сцену."""
        return await self.call_service("scene", "turn_on", entity_id)

    async def run_script(self, entity_id: str):
        """Запустить скрипт."""
        return await self.call_service("script", "turn_on", entity_id)

    # === Получение информации ===

    async def get_lights(self) -> List[Dict]:
        """Получить список всех осветителей."""
        states = await self.get_states()
        if "error" in states:
            return []
        return [s for s in states if s["entity_id"].startswith("light.")]

    async def get_switches(self) -> List[Dict]:
        """Получить список всех выключателей."""
        states = await self.get_states()
        if "error" in states:
            return []
        return [s for s in states if s["entity_id"].startswith("switch.")]

    async def get_sensors(self) -> List[Dict]:
        """Получить список всех датчиков."""
        states = await self.get_states()
        if "error" in states:
            return []
        return [s for s in states if s["entity_id"].startswith("sensor.")]

    async def get_cameras(self) -> List[Dict]:
        """Получить список камер."""
        states = await self.get_states()
        if "error" in states:
            return []
        return [s for s in states if s["entity_id"].startswith("camera.")]

    # === Обработка голосовых команд ===

    async def handle_command(self, command: str) -> Dict:
        """Обработка голосовых команд для умного дома."""
        cmd = command.lower()

        # Свет
        if "включи свет" in cmd or "зажги свет" in cmd:
            lights = await self.get_lights()
            for light in lights:
                await self.turn_on_light(light["entity_id"])
            return {"response": f"Включаю {len(lights)} осветителей."}

        elif "выключи свет" in cmd or "погаси свет" in cmd:
            lights = await self.get_lights()
            for light in lights:
                await self.turn_off_light(light["entity_id"])
            return {"response": "Выключаю весь свет."}

        # Температура
        elif "температуру" in cmd and any(c in cmd for c in ["20", "21", "22", "23", "24", "25"]):
            import re
            match = re.search(r'(\d+)', cmd)
            if match:
                temp = float(match.group(1))
                states = await self.get_states()
                climates = [s for s in states if s["entity_id"].startswith("climate.")]
                for climate in climates:
                    await self.set_temperature(climate["entity_id"], temp)
                return {"response": f"Устанавливаю температуру {temp} градусов."}

        # Сцены
        elif "сцену" in cmd:
            states = await self.get_states()
            scenes = [s for s in states if s["entity_id"].startswith("scene.")]
            if scenes:
                await self.activate_scene(scenes[0]["entity_id"])
                return {"response": f"Активирую сцену {scenes[0]['attributes'].get('friendly_name', '')}."}

        return {"response": "Не понимаю команду для умного дома."}
