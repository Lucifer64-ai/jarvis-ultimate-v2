"""
Модуль организации файлов JARVIS (стиль Железного Человека)
- Автоматическая сортировка скачанных файлов по категориям
- Наблюдение за папками в реальном времени
- Настраиваемые правила классификации
"""

import os
import shutil
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class FileOrganizer:
    """Модуль автоматической организации файлов для JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Конфигурация
        config = brain.config.get("file_organizer", {})
        self.enabled = config.get("enabled", True)
        self.watch_downloads = config.get("watch_downloads", True)
        self.auto_organize = config.get("auto_organize", False)  # Авто-сортировка без подтверждения
        self.downloads_folder = Path.home() / "Downloads"
        self.custom_folder = Path(config.get("target_folder", str(self.downloads_folder)))

        # Состояние наблюдения
        self.observer: Optional[threading.Thread] = None
        self.watchdog_observer: Optional[object] = None
        self.running = False

        # Категории файлов и их расширения
        self.categories: Dict[str, List[str]] = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
            "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
            "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "code": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml", ".yaml", ".yml"],
            "installers": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".AppImage"],
            "torrents": [".torrent"],
        }

        # Подкатегории внутри каждой категории
        self.subfolder_structure = config.get("subfolder_structure", True)

        self._load_rules()

    def _load_rules(self):
        """Загрузка пользовательских правил из конфига."""
        rules = self.brain.config.get("file_organizer", {}).get("custom_categories", {})
        for category, extensions in rules.items():
            self.categories[category] = [ext.lower() for ext in extensions]

    def get_category_for_file(self, file_path: Path) -> str:
        """Определить категорию файла по расширению."""
        ext = file_path.suffix.lower()
        for category, extensions in self.categories.items():
            if ext in extensions:
                return category
        return "other"

    def organize_folder(self, folder_path: Optional[str] = None) -> Dict:
        """Отсортировать файлы в указанной папке."""
        if not self.enabled:
            return {"status": "error", "message": "Организатор файлов отключен"}

        target = Path(folder_path) if folder_path else self.custom_folder
        if not target.exists() or not target.is_dir():
            return {"status": "error", "message": f"Папка не найдена: {target}"}

        moved = 0
        errors = 0
        results = []

        try:
            for item in target.iterdir():
                # Пропускаем папки и скрытые файлы
                if item.is_dir() or item.name.startswith('.'):
                    continue

                category = self.get_category_for_file(item)
                dest_folder = target / category

                if self.subfolder_structure:
                    dest_folder = dest_folder / item.suffix.lstrip('.').upper() if item.suffix else dest_folder / "no_extension"

                dest_folder.mkdir(parents=True, exist_ok=True)

                dest_path = dest_folder / item.name

                # Обработка дубликатов
                if dest_path.exists():
                    stem = item.stem
                    suffix = item.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = dest_folder / f"{stem}_{counter}{suffix}"
                        counter += 1

                try:
                    shutil.move(str(item), str(dest_path))
                    moved += 1
                    results.append({"file": item.name, "category": category, "destination": str(dest_path)})
                except Exception as e:
                    errors += 1
                    self.logger.error(f"Ошибка перемещения {item.name}: {e}")

        except Exception as e:
            return {"status": "error", "message": str(e)}

        self.logger.info(f"Организовано файлов: {moved}, ошибок: {errors}")
        return {
            "status": "ok",
            "folder": str(target),
            "moved": moved,
            "errors": errors,
            "results": results
        }

    def get_downloads_status(self) -> Dict:
        """Получить состояние папки загрузок."""
        folder = self.downloads_folder if self.watch_downloads else self.custom_folder
        if not folder.exists():
            return {"status": "error", "message": f"Папка не найдена: {folder}"}

        files = []
        try:
            for item in folder.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    category = self.get_category_for_file(item)
                    files.append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "category": category,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return {
            "status": "ok",
            "folder": str(folder),
            "files_count": len(files),
            "files": files
        }

    def start_watching(self) -> Dict:
        """Запуск наблюдения за папкой загрузок."""
        if not self.enabled:
            return {"status": "error", "message": "Организатор файлов отключен"}

        if not WATCHDOG_AVAILABLE:
            return {"status": "error", "message": "watchdog не установлен"}

        if self.running:
            return {"status": "ok", "message": "Наблюдение уже запущено"}

        self.running = True

        class DownloadHandler(FileSystemEventHandler):
            def __init__(self, organizer):
                self.organizer = organizer

            def on_created(self, event):
                if not event.is_directory and self.organizer.running:
                    # Небольшая задержка, чтобы файл успел записаться
                    threading.Timer(2.0, self._organize_file, args=[event.src_path]).start()

            def _organize_file(self, file_path: str):
                path = Path(file_path)
                if not path.exists():
                    return
                category = self.organizer.get_category_for_file(path)
                dest_folder = self.organizer.custom_folder / category
                dest_folder.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.move(str(path), str(dest_folder / path.name))
                    self.organizer.logger.info(f"Авто-организация: {path.name} -> {category}")
                except Exception as e:
                    self.organizer.logger.error(f"Ошибка авто-организации {path.name}: {e}")

        handler = DownloadHandler(self)
        self.watchdog_observer = Observer()
        self.watchdog_observer.schedule(handler, str(self.custom_folder), recursive=False)
        self.watchdog_observer.start()

        self.logger.info(f"Наблюдение за папкой запущено: {self.custom_folder}")
        return {"status": "ok", "message": f"Наблюдение за {self.custom_folder} запущено"}

    def stop_watching(self) -> Dict:
        """Остановка наблюдения."""
        if self.watchdog_observer:
            self.watchdog_observer.stop()
            self.watchdog_observer.join(timeout=2.0)
            self.watchdog_observer = None
        self.running = False
        self.logger.info("Наблюдение остановлено")
        return {"status": "ok", "message": "Наблюдение остановлено"}

    def add_category(self, category: str, extensions: List[str]) -> Dict:
        """Добавить новую категорию файлов."""
        self.categories[category] = [ext.lower() for ext in extensions]
        self.logger.info(f"Добавлена категория: {category} -> {extensions}")
        return {"status": "ok", "message": f"Категория '{category}' добавлена"}

    def remove_category(self, category: str) -> Dict:
        """Удалить категорию."""
        if category in self.categories:
            del self.categories[category]
            return {"status": "ok", "message": f"Категория '{category}' удалена"}
        return {"status": "error", "message": f"Категория '{category}' не найдена"}

    def list_categories(self) -> Dict:
        """Список всех категорий."""
        return {
            "status": "ok",
            "categories": self.categories
        }

    def get_status(self) -> Dict:
        """Получить статус организатора файлов."""
        return {
            "status": "ok",
            "enabled": self.enabled,
            "watching": self.running,
            "folder": str(self.custom_folder),
            "watch_downloads": self.watch_downloads,
            "auto_organize": self.auto_organize,
            "watchdog_available": WATCHDOG_AVAILABLE,
            "categories_count": len(self.categories)
        }
