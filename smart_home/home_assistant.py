"""
½µ³°¸ JARVIS  Home Assistant
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
import json
import logging


class HomeAssistantIntegration:
    """голосовые ¼½¼ ´¾¼¾¼ µµ· Home Assistant."""

    def __init__(self, brain):
        self.brain = brain
        
        # §µ½¸µ из ¿µµ¼µ½½ ¾º¶µ½¸
        self.url = brain.config.home_assistant_url
        self.token = brain.config.home_assistant_token
        
        if self.url and self.token:
            self.brain.logger.info(f"Home Assistant ¿¾´º»µ½: {self.url}")
        else:
            self.brain.logger.warning("Home Assistant ни на¾µ½. ¾±°²µ HOME_ASSISTANT_URL ¸ HOME_ASSISTANT_TOKEN ² .env")
        
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        """¡¾·´°½¸µ HTTP µ¸¸."""
        if not self.url or not self.token:
            raise Exception("Home Assistant ни на¾µ½")
        
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
            )

    async def close(self):
        """°º¸µ µ¸¸."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_states(self) -> Dict:
        """ошибки ²µ ¾¾½¸ ¾¹²."""
        await self._ensure_session()
        try:
            async with self.session.get(f"{self.url}/api/states") as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"Status {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

    async def get_entity(self, entity_id: str) -> Dict:
        """ошибки ¾¾½¸µ º¾½ºµ½¾³¾ ¾¹²°."""
        await self._ensure_session()
        try:
            async with self.session.get(f"{self.url}/api/states/{entity_id}") as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"Status {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

    async def call_service(self, domain: str, service: str, entity_id: str = None, **kwargs) -> Dict:
        """·¾² µ²¸° Home Assistant."""
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

    # === голосовые ¾²µµ½¸µ¼ ===

    async def turn_on_light(self, entity_id: str, brightness: int = None, color: tuple = None):
        """º»¸ ²µ."""
        kwargs = {}
        if brightness:
            kwargs["brightness"] = int(brightness * 2.55)
        if color:
            kwargs["rgb_color"] = color
        
        return await self.call_service("light", "turn_on", entity_id, **kwargs)

    async def turn_off_light(self, entity_id: str):
        """º»¸ ²µ."""
        return await self.call_service("light", "turn_off", entity_id)

    async def set_brightness(self, entity_id: str, brightness: int):
        """£°½¾²¸ º¾."""
        return await self.turn_on_light(entity_id, brightness=brightness)

    async def set_color(self, entity_id: str, r: int, g: int, b: int):
        """£°½¾²¸ ²µ."""
        return await self.turn_on_light(entity_id, color=(r, g, b))

    # === голосовые º»¸¼°¾¼ ===

    async def set_temperature(self, entity_id: str, temperature: float):
        """£°½¾²¸ µ¼¿µ°."""
        return await self.call_service(
            "climate", "set_temperature",
            entity_id, temperature=temperature
        )

    async def set_hvac_mode(self, entity_id: str, mode: str):
        """£°½¾²¸ µ¶¸¼ HVAC."""
        return await self.call_service(
            "climate", "set_hvac_mode",
            entity_id, hvac_mode=mode
        )

    # === голосовые ¼µ´¸° ===

    async def media_play(self, entity_id: str):
        """¾¿¾из²µ¸ ¼µ´¸°."""
        return await self.call_service("media_player", "media_play", entity_id)

    async def media_pause(self, entity_id: str):
        """°·° ¼µ´¸°."""
        return await self.call_service("media_player", "media_pause", entity_id)

    async def media_stop(self, entity_id: str):
        """°½¾²¸ ¼µ´¸°."""
        return await self.call_service("media_player", "media_stop", entity_id)

    async def set_volume(self, entity_id: str, volume: float):
        """£°½¾²¸ ³¾¼º¾."""
        return await self.call_service(
            "media_player", "volume_set",
            entity_id, volume_level=volume
        )

    # === голосовые ·°¼º°¼¸ ===

    async def lock(self, entity_id: str):
        """°±»¾º¸¾²° ·°¼¾º."""
        return await self.call_service("lock", "lock", entity_id)

    async def unlock(self, entity_id: str):
        """ °·±»¾º¸¾²° ·°¼¾º."""
        return await self.call_service("lock", "unlock", entity_id)

    # === ¡µ½ ¸ º¸¿ ===

    async def activate_scene(self, entity_id: str):
        """º¸²¸¾²° µ½."""
        return await self.call_service("scene", "turn_on", entity_id)

    async def run_script(self, entity_id: str):
        """°¿¸ º¸¿."""
        return await self.call_service("script", "turn_on", entity_id)

    # === ¾»µ½¸µ ¸½¾¼°¸¸ ===

    async def get_lights(self) -> List[Dict]:
        """ошибки ¿¸¾º ²µ ²µ¸»½¸º¾²."""
        states = await self.get_states()
        if "error" in states:
            return []
        return [s for s in states if s["entity_id"].startswith("light.")]

    async def get_switches(self) -> List[Dict]:
        """ошибки ¿¸¾º ²µ ²º»°µ»µ¹."""
        states = await self.get_states()
        if "error" in states:
            return []
        return [s for s in states if s["entity_id"].startswith("switch.")]

    async def get_sensors(self) -> List[Dict]:
        """ошибки ¿¸¾º ²µ ´°¸º¾²."""
        states = await self.get_states()
        if "error" in states:
            return []
        return [s for s in states if s["entity_id"].startswith("sensor.")]

    async def get_cameras(self) -> List[Dict]:
        """ошибки ¿¸¾º º°¼µ."""
        states = await self.get_states()
        if "error" in states:
            return []
        return [s for s in states if s["entity_id"].startswith("camera.")]

    # === ±°±¾º° ³¾»¾¾² команд ===

    async def handle_command(self, command: str) -> Dict:
        """±°±¾º° ³¾»¾¾²¾¹ команд для ¼½¾³¾ ´¾¼°."""
        cmd = command.lower()
        
        # ¡²µ
        if "²º»¸ ²µ" in cmd or "·°¶³¸ ²µ" in cmd:
            lights = await self.get_lights()
            for light in lights:
                await self.turn_on_light(light["entity_id"])
            return {"response": f"º»° {len(lights)} ²µ¸»½¸º¾²."}
        
        elif "²º»¸ ²µ" in cmd or "¿¾¸ ²µ" in cmd:
            lights = await self.get_lights()
            for light in lights:
                await self.turn_off_light(light["entity_id"])
            return {"response": "º»° ²µ ²µ."}
        
        # ¢µ¼¿µ°°
        elif "µ¼¿µ°" in cmd and any(c in cmd for c in ["20", "21", "22", "23", "24", "25"]):
            import re
            match = re.search(r'(\d+)', cmd)
            if match:
                temp = float(match.group(1))
                states = await self.get_states()
                climates = [s for s in states if s["entity_id"].startswith("climate.")]
                for climate in climates:
                    await self.set_temperature(climate["entity_id"], temp)
                return {"response": f"£°на²»¸²° µ¼¿µ° {temp} ³°´¾²."}
        
        # ¡µ½
        elif "µ½" in cmd:
            states = await self.get_states()
            scenes = [s for s in states if s["entity_id"].startswith("scene.")]
            if scenes:
                await self.activate_scene(scenes[0]["entity_id"])
                return {"response": f"º¸²¸ µ½ {scenes[0]['attributes'].get('friendly_name', '')}."}
        
        return {"response": "µ ¿¾½¸¼° команд для ¼½¾³¾ ´¾¼°."}
