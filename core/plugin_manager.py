"""
Менеджер плагинов JARVIS
"""

import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional


class PluginManager:
    """Загрузка и управление плагинами."""

    def __init__(self, brain):
        self.brain = brain
        self.plugins_dir = Path("plugins")
        self.plugins_dir.mkdir(exist_ok=True)
        self.loaded: Dict[str, object] = {}

    def discover_plugins(self) -> List[str]:
        plugins = []
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and (item / "plugin.py").exists():
                plugins.append(item.name)
            elif item.suffix == ".py" and item.name != "__init__.py":
                plugins.append(item.stem)
        return plugins

    def load_plugin(self, name: str) -> Dict:
        try:
            plugin_path = self.plugins_dir / name
            if plugin_path.is_dir():
                spec = importlib.util.spec_from_file_location(
                    name, str(plugin_path / "plugin.py")
                )
            else:
                spec = importlib.util.spec_from_file_location(
                    name, str(self.plugins_dir / f"{name}.py")
                )

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "setup"):
                plugin = module.setup(self.brain)
                self.loaded[name] = plugin
                self.brain.logger.info(f"Плагин '{name}' загружен")
                return {"status": "ok", "name": name}
            else:
                return {"status": "error", "message": "Плагин не имеет функции setup()"}
        except Exception as e:
            self.brain.logger.error(f"Ошибка загрузки плагина {name}: {e}")
            return {"status": "error", "message": str(e)}


    def load_plugins(self) -> List[Dict]:
        """Загружает все обнаруженные плагины."""
        results = []
        plugins = self.discover_plugins()
        for name in plugins:
            result = self.load_plugin(name)
            results.append(result)
        return results

    def unload_plugin(self, name: str) -> Dict:
        if name in self.loaded:
            plugin = self.loaded[name]
            if hasattr(plugin, "shutdown"):
                plugin.shutdown()
            del self.loaded[name]
            return {"status": "ok"}
        return {"status": "error", "message": "Плагин не загружен"}

    def list_plugins(self) -> List[Dict]:
        available = self.discover_plugins()
        return [
            {"name": name, "loaded": name in self.loaded}
            for name in available
        ]

    def get_plugin(self, name: str) -> Optional[object]:
        return self.loaded.get(name)
