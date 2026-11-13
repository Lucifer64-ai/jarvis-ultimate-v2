"""
¡µ½ ¸ °²¾¼°¸·°¸¸ ¼½¾³¾ ´¾¼°
"""

from typing import Dict, List
import json
from pathlib import Path


class SceneManager:
    """£¿°²»µ½¸µ µ½°¼¸ ¼½¾³¾ ´¾¼°."""

    def __init__(self, brain):
        self.brain = brain
        self.ha = brain.smart_home.get("home_assistant") if hasattr(brain, "smart_home") else None
        self.custom_scenes_file = Path("data/custom_scenes.json")
        self.custom_scenes_file.parent.mkdir(exist_ok=True)
        self.custom_scenes = self._load_scenes()

    def _load_scenes(self) -> Dict:
        """°³·º° ¿¾»·¾²°µ»º¸ µ½."""
        if self.custom_scenes_file.exists():
            with open(self.custom_scenes_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_scenes(self):
        """¡¾°½µ½¸µ µ½."""
        with open(self.custom_scenes_file, "w", encoding="utf-8") as f:
            json.dump(self.custom_scenes, f, ensure_ascii=False, indent=2)

    def create_scene(self, name: str, actions: List[Dict]) -> Dict:
        """¡¾·´° ¿¾»·¾²°µ»º µ½."""
        self.custom_scenes[name] = {"actions": actions}
        self._save_scenes()
        return {"status": "ok", "name": name}

    async def activate_scene(self, name: str) -> Dict:
        """º¸²¸¾²° µ½."""
        # ¾²µ¸ ¿¾»·¾²°µ»º¸µ µ½
        if name in self.custom_scenes:
            scene = self.custom_scenes[name]
            results = []
            for action in scene["actions"]:
                result = await self._execute_action(action)
                results.append(result)
            return {"status": "ok", "scene": name, "results": results}
        
        # ¾¸º ² Home Assistant
        states = await self.ha.get_states()
        for state in states:
            if state["entity_id"].startswith("scene."):
                friendly = state["attributes"].get("friendly_name", "").lower()
                if name.lower() in friendly or name.lower() in state["entity_id"]:
                    return await self.ha.activate_scene(state["entity_id"])
        
        return {"status": "error", "message": f"¡µ½° '{name}' ½µ ½°¹´µ½°"}

    async def _execute_action(self, action: Dict) -> Dict:
        """¿¾»½¸ ´µ¹²¸µ µ½."""
        domain = action.get("domain")
        service = action.get("service")
        entity_id = action.get("entity_id")
        data = action.get("data", {})
        
        return await self.ha.call_service(domain, service, entity_id, **data)

    def list_scenes(self) -> List[str]:
        """¡¿¸¾º ¿¾»·¾²°µ»º¸ µ½."""
        return list(self.custom_scenes.keys())

    def delete_scene(self, name: str) -> Dict:
        """£´°»¸ µ½."""
        if name in self.custom_scenes:
            del self.custom_scenes[name]
            self._save_scenes()
            return {"status": "ok"}
        return {"status": "error", "message": "¡µ½° ½µ ½°¹´µ½°"}
