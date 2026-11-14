"""
Управление устройствами умного дома
"""

from typing import Dict, List, Optional
import asyncio


class DeviceManager:
    """Управление устройствами через Home Assistant."""

    def __init__(self, brain):
        self.brain = brain
        self.ha = brain.smart_home.get("home_assistant") if hasattr(brain, "smart_home") else None
        self.device_aliases = {}

    def set_alias(self, name: str, entity_id: str):
        """Установить псевдоним для устройства."""
        self.device_aliases[name.lower()] = entity_id

    def get_entity_id(self, name: str) -> Optional[str]:
        """Получить entity_id по имени."""
        return self.device_aliases.get(name.lower())

    async def turn_on(self, name: str) -> Dict:
        """Включить устройство."""
        entity_id = self.get_entity_id(name)
        if not entity_id:
            return {"status": "error", "message": f"Устройство '{name}' не найдено"}

        domain = entity_id.split(".")[0]
        return await self.ha.call_service(domain, "turn_on", entity_id)

    async def turn_off(self, name: str) -> Dict:
        """Выключить устройство."""
        entity_id = self.get_entity_id(name)
        if not entity_id:
            return {"status": "error", "message": f"Устройство '{name}' не найдено"}

        domain = entity_id.split(".")[0]
        return await self.ha.call_service(domain, "turn_off", entity_id)

    async def get_status(self, name: str) -> Dict:
        """Получить статус устройства."""
        entity_id = self.get_entity_id(name)
        if not entity_id:
            return {"status": "error", "message": f"Устройство '{name}' не найдено"}

        return await self.ha.get_entity(entity_id)

    async def list_devices(self) -> List[Dict]:
        """Список всех устройств."""
        states = await self.ha.get_states()
        if "error" in states:
            return []

        devices = []
        for state in states:
            domain = state["entity_id"].split(".")[0]
            if domain in ["light", "switch", "climate", "media_player", "lock", "sensor", "camera"]:
                devices.append({
                    "entity_id": state["entity_id"],
                    "name": state["attributes"].get("friendly_name", state["entity_id"]),
                    "state": state["state"],
                    "domain": domain,
                })

        return devices
