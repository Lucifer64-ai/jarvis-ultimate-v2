"""
Мониторинг датчиков умного дома
"""

from typing import Dict, List, Optional
import asyncio


class SensorMonitor:
    """Мониторинг датчиков умного дома."""

    def __init__(self, brain):
        self.brain = brain
        self.ha = brain.smart_home.get("home_assistant") if hasattr(brain, "smart_home") else None
        self.alerts = {}

    async def get_all_sensors(self) -> List[Dict]:
        """Получить все датчики."""
        states = await self.ha.get_states()
        if "error" in states:
            return []

        sensors = []
        for state in states:
            if state["entity_id"].startswith("sensor."):
                sensors.append({
                    "entity_id": state["entity_id"],
                    "name": state["attributes"].get("friendly_name", ""),
                    "value": state["state"],
                    "unit": state["attributes"].get("unit_of_measurement", ""),
                    "device_class": state["attributes"].get("device_class", ""),
                })

        return sensors

    async def get_temperature(self) -> Dict:
        """Получить температуру."""
        sensors = await self.get_all_sensors()
        temps = [s for s in sensors if s.get("device_class") == "temperature"]
        if temps:
            return {
                "sensors": temps,
                "average": sum(float(t["value"]) for t in temps if t["value"] not in ["unknown", "unavailable"]) / len(temps) if temps else 0
            }
        return {"sensors": [], "average": 0}

    async def get_humidity(self) -> Dict:
        """Получить влажность."""
        sensors = await self.get_all_sensors()
        hums = [s for s in sensors if s.get("device_class") == "humidity"]
        return {"sensors": hums}

    async def get_motion_sensors(self) -> List[Dict]:
        """Датчики движения."""
        sensors = await self.get_all_sensors()
        return [s for s in sensors if s.get("device_class") == "motion"]

    async def get_door_sensors(self) -> List[Dict]:
        """Датчики дверей/окон."""
        sensors = await self.get_all_sensors()
        return [s for s in sensors if s.get("device_class") in ["door", "window", "opening"]]

    def set_alert(self, name: str, entity_id: str, condition: str, threshold: float):
        """Настроить оповещение."""
        self.alerts[name] = {
            "entity_id": entity_id,
            "condition": condition,  # "above", "below"
            "threshold": threshold,
            "active": True
        }

    async def check_alerts(self) -> List[Dict]:
        """Проверить оповещения."""
        triggered = []
        for name, alert in self.alerts.items():
            if not alert["active"]:
                continue

            entity = await self.ha.get_entity(alert["entity_id"])
            if "error" in entity:
                continue

            try:
                value = float(entity["state"])
            except (ValueError, TypeError):
                continue

            if alert["condition"] == "above" and value > alert["threshold"]:
                triggered.append({
                    "name": name,
                    "entity_id": alert["entity_id"],
                    "value": value,
                    "threshold": alert["threshold"],
                    "message": f"{name}: Значение {value} выше порога {alert['threshold']}"
                })
            elif alert["condition"] == "below" and value < alert["threshold"]:
                triggered.append({
                    "name": name,
                    "entity_id": alert["entity_id"],
                    "value": value,
                    "threshold": alert["threshold"],
                    "message": f"{name}: Значение {value} ниже порога {alert['threshold']}"
                })

        return triggered
