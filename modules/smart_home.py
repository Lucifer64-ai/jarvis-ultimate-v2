"""
Модуль умного дома JARVIS (стиль Железного Человека)
- Интеграция с Home Assistant
- Поддержка MQTT
- Управление светом, климатом, безопасностью
"""

import json
import threading
from typing import Dict, List, Optional
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False


class SmartHome:
    """Модуль управления умным домом для JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Конфигурация
        sh_config = brain.config.get("smart_home", {})
        self.enabled = sh_config.get("enabled", False)
        self.provider = sh_config.get("provider", "home_assistant")  # home_assistant, mqtt, both
        self.ha_url = sh_config.get("url", "http://homeassistant.local:8123")
        self.ha_token = sh_config.get("token", "")
        self.mqtt_broker = sh_config.get("mqtt_broker", "localhost")
        self.mqtt_port = sh_config.get("mqtt_port", 1883)
        self.mqtt_user = sh_config.get("mqtt_user", "")
        self.mqtt_pass = sh_config.get("mqtt_pass", "")

        # Состояние устройств
        self.devices: Dict[str, Dict] = {}
        self.mqtt_client = None
        self.mqtt_connected = False

        # Инициализация
        self._init_connections()

    def _init_connections(self):
        """Инициализация подключений к умному дому."""
        if not self.enabled:
            self.logger.info("Умный дом отключен в конфиге")
            return

        if self.provider in ("home_assistant", "both") and REQUESTS_AVAILABLE:
            self._init_home_assistant()

        if self.provider in ("mqtt", "both") and MQTT_AVAILABLE:
            self._init_mqtt()

    def _init_home_assistant(self):
        """Инициализация подключения к Home Assistant."""
        try:
            headers = {"Authorization": f"Bearer {self.ha_token}"}
            response = requests.get(f"{self.ha_url}/api/states", headers=headers, timeout=5)
            if response.status_code == 200:
                states = response.json()
                for state in states:
                    entity_id = state.get("entity_id", "")
                    self.devices[entity_id] = {
                        "state": state.get("state"),
                        "attributes": state.get("attributes", {}),
                        "last_changed": state.get("last_changed"),
                        "source": "home_assistant"
                    }
                self.logger.info(f"Home Assistant подключен. Устройств: {len(self.devices)}")
            else:
                self.logger.warning(f"Home Assistant недоступен: HTTP {response.status_code}")
        except Exception as e:
            self.logger.warning(f"Home Assistant не подключен: {e}")

    def _init_mqtt(self):
        """Инициализация MQTT клиента."""
        try:
            self.mqtt_client = mqtt.Client()
            if self.mqtt_user:
                self.mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_pass)

            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message

            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            self.logger.info(f"MQTT подключение запущено: {self.mqtt_broker}:{self.mqtt_port}")
        except Exception as e:
            self.logger.warning(f"MQTT не подключен: {e}")

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback подключения MQTT."""
        if rc == 0:
            self.mqtt_connected = True
            client.subscribe("homeassistant/#")
            client.subscribe("jarvis/#")
            self.logger.info("MQTT подключен")
        else:
            self.logger.warning(f"MQTT ошибка подключения: {rc}")

    def _on_mqtt_message(self, client, userdata, msg):
        """Callback получения сообщения MQTT."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            self.logger.debug(f"MQTT {topic}: {payload}")

            # Обновляем состояние устройства
            entity_id = topic.replace("homeassistant/", "").replace("jarvis/", "")
            try:
                data = json.loads(payload)
                self.devices[entity_id] = {
                    "state": data.get("state", payload),
                    "attributes": data,
                    "source": "mqtt",
                    "topic": topic
                }
            except json.JSONDecodeError:
                self.devices[entity_id] = {
                    "state": payload,
                    "attributes": {},
                    "source": "mqtt",
                    "topic": topic
                }
        except Exception as e:
            self.logger.error(f"Ошибка обработки MQTT сообщения: {e}")

    # === Управление устройствами ===

    def get_devices(self) -> Dict:
        """Получить список всех устройств."""
        return {
            "status": "ok",
            "devices": self.devices,
            "count": len(self.devices),
            "enabled": self.enabled,
            "provider": self.provider
        }

    def get_device(self, entity_id: str) -> Dict:
        """Получить состояние конкретного устройства."""
        if entity_id in self.devices:
            return {"status": "ok", "device": self.devices[entity_id]}
        return {"status": "error", "message": f"Устройство {entity_id} не найдено"}

    def turn_on(self, entity_id: str) -> Dict:
        """Включить устройство."""
        return self._control_device(entity_id, "on")

    def turn_off(self, entity_id: str) -> Dict:
        """Выключить устройство."""
        return self._control_device(entity_id, "off")

    def toggle(self, entity_id: str) -> Dict:
        """Переключить устройство."""
        return self._control_device(entity_id, "toggle")

    def _control_device(self, entity_id: str, action: str) -> Dict:
        """Управление устройством."""
        if not self.enabled:
            return {"status": "error", "message": "Умный дом отключен"}

        # Home Assistant API
        if self.provider in ("home_assistant", "both") and REQUESTS_AVAILABLE:
            try:
                headers = {
                    "Authorization": f"Bearer {self.ha_token}",
                    "Content-Type": "application/json"
                }
                service = "turn_on" if action == "on" else "turn_off" if action == "off" else "toggle"
                domain = entity_id.split(".")[0] if "." in entity_id else "homeassistant"
                url = f"{self.ha_url}/api/services/{domain}/{service}"

                response = requests.post(
                    url, headers=headers,
                    json={"entity_id": entity_id}, timeout=5
                )
                if response.status_code in (200, 201):
                    self.logger.info(f"Home Assistant: {entity_id} -> {action}")
                    return {"status": "ok", "message": f"{entity_id} переведен в состояние {action}"}
                else:
                    return {"status": "error", "message": f"Home Assistant ошибка: {response.status_code}"}
            except Exception as e:
                self.logger.error(f"Ошибка управления Home Assistant: {e}")

        # MQTT
        if self.provider in ("mqtt", "both") and self.mqtt_client and self.mqtt_connected:
            try:
                topic = f"jarvis/{entity_id}/set"
                payload = json.dumps({"state": action})
                self.mqtt_client.publish(topic, payload)
                self.logger.info(f"MQTT: {topic} -> {action}")
                return {"status": "ok", "message": f"Команда отправлена через MQTT: {entity_id} -> {action}"}
            except Exception as e:
                self.logger.error(f"Ошибка MQTT управления: {e}")

        return {"status": "error", "message": "Нет доступных подключений к умному дому"}

    def control_light(self, entity_id: str, state: str, brightness: Optional[int] = None,
                      color: Optional[str] = None) -> Dict:
        """Управление освещением с яркостью и цветом."""
        if not self.enabled:
            return {"status": "error", "message": "Умный дом отключен"}

        if self.provider in ("home_assistant", "both") and REQUESTS_AVAILABLE:
            try:
                headers = {
                    "Authorization": f"Bearer {self.ha_token}",
                    "Content-Type": "application/json"
                }
                data = {"entity_id": entity_id}
                if state:
                    data["state"] = state
                if brightness is not None:
                    data["brightness_pct"] = brightness
                if color:
                    data["color_name"] = color

                response = requests.post(
                    f"{self.ha_url}/api/services/light/turn_{state}",
                    headers=headers, json=data, timeout=5
                )
                if response.status_code in (200, 201):
                    return {"status": "ok", "message": f"Освещение {entity_id} установлено: {state}"}
                return {"status": "error", "message": f"Ошибка: {response.status_code}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        return {"status": "error", "message": "Home Assistant не доступен"}

    def set_climate(self, entity_id: str, temperature: float, hvac_mode: str = "heat") -> Dict:
        """Управление климатом (кондиционер/отопление)."""
        if not self.enabled:
            return {"status": "error", "message": "Умный дом отключен"}

        if self.provider in ("home_assistant", "both") and REQUESTS_AVAILABLE:
            try:
                headers = {
                    "Authorization": f"Bearer {self.ha_token}",
                    "Content-Type": "application/json"
                }
                data = {
                    "entity_id": entity_id,
                    "temperature": temperature,
                    "hvac_mode": hvac_mode
                }
                response = requests.post(
                    f"{self.ha_url}/api/services/climate/set_temperature",
                    headers=headers, json=data, timeout=5
                )
                if response.status_code in (200, 201):
                    return {"status": "ok", "message": f"Температура {entity_id} установлена на {temperature}°C"}
                return {"status": "error", "message": f"Ошибка: {response.status_code}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        return {"status": "error", "message": "Home Assistant не доступен"}

    def get_status(self) -> Dict:
        """Получить статус умного дома."""
        return {
            "status": "ok",
            "enabled": self.enabled,
            "provider": self.provider,
            "devices_count": len(self.devices),
            "home_assistant_available": bool(self.ha_url and self.ha_token and REQUESTS_AVAILABLE),
            "mqtt_connected": self.mqtt_connected,
            "devices": list(self.devices.keys())[:20]  # Первые 20 для краткости
        }
