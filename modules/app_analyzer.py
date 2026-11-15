"""
App Analyzer Module - Анализ приложений на ПК
JARVIS сканирует, анализирует и разбирает приложения
"""

import os
import json
import subprocess
import psutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import winreg
except ImportError:
    winreg = None


class AppAnalyzer:
    """Модуль анализа приложений на ПК."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.config = brain.config

        # База данных приложений
        self.apps_db = {}
        self.db_path = Path("data/apps_database.json")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Первичная загрузка базы
        self._load_database()

        # Пути для сканирования
        self.scan_paths = [
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")),
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")),
            Path(os.environ.get("LOCALAPPDATA", "")),
            Path(os.environ.get("APPDATA", "")),
            Path(os.path.expanduser("~\\Desktop")),
            Path(os.environ.get("USERPROFILE", "")),
        ]

        # Исполняемые расширения
        self.executable_extensions = {".exe", ".msi", ".bat", ".cmd", ".ps1", ".com"}

        # Расширения документов для анализа
        self.document_extensions = {
            ".txt", ".md", ".json", ".xml", ".yaml", ".yml",
            ".ini", ".cfg", ".conf", ".log",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx",
            ".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h"
        }

        self.logger.info("Модуль анализа приложений инициализирован")

    def _load_database(self):
        """Загрузка базы данных приложений."""
        try:
            if self.db_path.exists():
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.apps_db = json.load(f)
                self.logger.info(f"Загружена база приложений: {len(self.apps_db)} записей")
            else:
                self.apps_db = {}
        except Exception as e:
            self.logger.error(f"Ошибка загрузки базы: {e}")
            self.apps_db = {}

    def _save_database(self):
        """Сохранение базы данных приложений."""
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.apps_db, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения базы: {e}")

    # === СКАНИРОВАНИЕ ===

    def scan_installed_apps(self) -> Dict:
        """Сканирование установленных приложений через реестр Windows."""
        if winreg is None:
            return {"status": "error", "message": "winreg недоступен (только для Windows)"}

        self.logger.info("Сканирование установленных приложений...")
        apps = []

        # Список веток для поиска
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]

        for hive, path in registry_keys:
            try:
                key = winreg.OpenKey(hive, path)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)

                        app_info = self._read_registry_app(subkey)
                        if app_info and app_info.get("name"):
                            apps.append(app_info)

                        winreg.CloseKey(subkey)
                        i += 1
                    except OSError:
                        break

                winreg.CloseKey(key)
            except Exception as e:
                self.logger.debug(f"Ошибка ветки {path}: {e}")

        # Обновление базы
        for app in apps:
            app_id = app.get("name", "").lower().replace(" ", "_")
            self.apps_db[app_id] = {
                **app,
                "last_seen": datetime.now().isoformat(),
                "analyzed": self.apps_db.get(app_id, {}).get("analyzed", False)
            }

        self._save_database()

        self.logger.info(f"Найдено {len(apps)} установленных приложений")
        return {
            "status": "ok",
            "count": len(apps),
            "apps": apps
        }

    def _read_registry_app(self, key) -> Optional[Dict]:
        """Чтение информации об приложении из реестра."""
        try:
            name = winreg.QueryValueEx(key, "DisplayName")[0]
        except (OSError, FileNotFoundError):
            return None

        app_info = {"name": name}

        # Дополнительные поля
        fields = {
            "DisplayVersion": "version",
            "Publisher": "publisher",
            "InstallDate": "install_date",
            "InstallLocation": "install_path",
            "UninstallString": "uninstall_string",
            "DisplayIcon": "icon_path",
            "EstimatedSize": "size_kb",
            "URLInfoAbout": "website",
            "HelpLink": "help_link",
        }

        for reg_name, field_name in fields.items():
            try:
                value = winreg.QueryValueEx(key, reg_name)[0]
                app_info[field_name] = value
            except (OSError, FileNotFoundError):
                pass

        return app_info

    def scan_executables(self, directory: str = None) -> Dict:
        """Сканирование исполняемых файлов в директориях."""
        self.logger.info("Сканирование исполняемых файлов...")
        executables = []

        paths_to_scan = [Path(directory)] if directory else self.scan_paths

        for scan_path in paths_to_scan:
            if not scan_path or not scan_path.exists():
                continue

            try:
                for item in scan_path.rglob("*"):
                    if item.suffix.lower() in self.executable_extensions:
                        exe_info = self._analyze_executable(item)
                        if exe_info:
                            executables.append(exe_info)
            except PermissionError:
                continue
            except Exception as e:
                self.logger.debug(f"Ошибка сканирования {scan_path}: {e}")

        return {
            "status": "ok",
            "count": len(executables),
            "executables": executables[:100]  # Ограничение
        }

    def _analyze_executable(self, path: Path) -> Optional[Dict]:
        """Анализ исполняемого файла."""
        try:
            stat = path.stat()

            info = {
                "name": path.stem,
                "path": str(path),
                "extension": path.suffix,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }

            # Версия файла (Windows)
            try:
                import win32api
                version_info = win32api.GetFileVersionInfo(str(path), "\\")
                if version_info:
                    info["file_version"] = str(version_info.get("FileVersion", ""))
                    info["product_version"] = str(version_info.get("ProductVersion", ""))
                    info["company"] = str(version_info.get("CompanyName", ""))
                    info["description"] = str(version_info.get("FileDescription", ""))
            except Exception:
                pass

            return info

        except Exception as e:
            self.logger.debug(f"Ошибка анализа {path}: {e}")
            return None

    # === ДЕТАЛЬНЫЙ АНАЛИЗ ===

    def analyze_app(self, app_name: str) -> Dict:
        """Детальный анализ конкретного приложения."""
        self.logger.info(f"Анализ приложения: {app_name}")

        app_id = app_name.lower().replace(" ", "_")

        # Поиск в базе
        app_data = self.apps_db.get(app_id)
        if not app_data:
            # Поиск по частичному совпадению
            for key, value in self.apps_db.items():
                if app_name.lower() in key or app_name.lower() in value.get("name", "").lower():
                    app_data = value
                    app_id = key
                    break

        if not app_data:
            return {"status": "error", "message": f"Приложение '{app_name}' не найдено"}

        # Детальный анализ
        analysis = {
            "name": app_data.get("name", app_name),
            "version": app_data.get("version", "неизвестно"),
            "publisher": app_data.get("publisher", "неизвестно"),
            "install_path": app_data.get("install_path", ""),
            "size_kb": app_data.get("size_kb", 0),
            "install_date": app_data.get("install_date", "неизвестно"),
        }

        # Анализ файлов приложения
        if analysis["install_path"] and Path(analysis["install_path"]).exists():
            analysis["files"] = self._analyze_app_files(Path(analysis["install_path"]))

        # Анализ процессов
        analysis["running"] = self._is_app_running(app_name)
        if analysis["running"]:
            analysis["processes"] = self._get_app_processes(app_name)

        # Анализ ресурсов
        if analysis["running"] and analysis.get("processes"):
            analysis["resource_usage"] = self._get_app_resource_usage(analysis["processes"])

        # Категоризация
        analysis["category"] = self._categorize_app(app_name, app_data)

        # Описание
        analysis["description"] = self._generate_app_description(analysis)

        # Обновление базы
        self.apps_db[app_id] = {
            **app_data,
            "analyzed": True,
            "last_analyzed": datetime.now().isoformat(),
            "analysis": analysis
        }
        self._save_database()

        return {"status": "ok", "analysis": analysis}

    def _analyze_app_files(self, app_path: Path) -> Dict:
        """Анализ файлов приложения."""
        files_info = {
            "total_files": 0,
            "total_size_mb": 0,
            "file_types": {},
            "config_files": [],
            "data_files": [],
            "executables": [],
        }

        try:
            for item in app_path.rglob("*"):
                if item.is_file():
                    files_info["total_files"] += 1
                    files_info["total_size_mb"] += item.stat().st_size / (1024 * 1024)

                    ext = item.suffix.lower()
                    files_info["file_types"][ext] = files_info["file_types"].get(ext, 0) + 1

                    if ext in {".ini", ".cfg", ".conf", ".json", ".xml", ".yaml", ".yml", ".toml"}:
                        files_info["config_files"].append(str(item.relative_to(app_path)))

                    elif ext in {".db", ".sqlite", ".dat", ".sav"}:
                        files_info["data_files"].append(str(item.relative_to(app_path)))

                    elif ext in self.executable_extensions:
                        files_info["executables"].append(str(item.relative_to(app_path)))

        except Exception as e:
            self.logger.debug(f"Ошибка анализа файлов {app_path}: {e}")

        files_info["total_size_mb"] = round(files_info["total_size_mb"], 2)
        return files_info

    def _is_app_running(self, app_name: str) -> bool:
        """Проверка, запущено ли приложение."""
        app_lower = app_name.lower()
        for proc in psutil.process_iter(["name"]):
            try:
                if app_lower in proc.info["name"].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def _get_app_processes(self, app_name: str) -> List[Dict]:
        """Получение информации о процессах приложения."""
        processes = []
        app_lower = app_name.lower()

        for proc in psutil.process_iter(["pid", "name", "exe", "status", "create_time"]):
            try:
                if app_lower in proc.info["name"].lower():
                    processes.append({
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "exe": proc.info["exe"],
                        "status": proc.info["status"],
                        "started": datetime.fromtimestamp(proc.info["create_time"]).isoformat()
                            if proc.info["create_time"] else None
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return processes

    def _get_app_resource_usage(self, processes: List[Dict]) -> Dict:
        """Получение информации об использовании ресурсов приложением."""
        total_cpu = 0.0
        total_memory_mb = 0.0

        for proc_info in processes:
            try:
                proc = psutil.Process(proc_info["pid"])
                total_cpu += proc.cpu_percent(interval=0.1)
                total_memory_mb += proc.memory_info().rss / (1024 * 1024)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            "cpu_percent": round(total_cpu, 1),
            "memory_mb": round(total_memory_mb, 1),
            "process_count": len(processes)
        }

    def _categorize_app(self, app_name: str, app_data: Dict) -> str:
        """Категоризация приложения."""
        name_lower = app_name.lower()

        categories = {
            "browser": ["chrome", "firefox", "edge", "opera", "brave", "safari", "браузер"],
            "messenger": ["telegram", "discord", "slack", "whatsapp", "viber", "skype", "teams"],
            "editor": ["code", "vscode", "notepad", "sublime", "atom", "vim", "notepad++"],
            "media": ["vlc", "spotify", "youtube", "netflix", "plex", "kodi", "itunes"],
            "game": ["steam", "epic", "origin", "gog", "ubisoft", "battle.net"],
            "dev": ["python", "node", "java", "git", "docker", "visual studio", "intellij", "pycharm"],
            "office": ["word", "excel", "powerpoint", "outlook", "libreoffice", "office"],
            "security": ["antivirus", "defender", "kaspersky", "norton", "malwarebytes", "avast"],
            "system": ["explorer", "task manager", "control panel", "settings", "ccleaner"],
            "cloud": ["dropbox", "onedrive", "google drive", "yandex disk"],
        }

        for category, keywords in categories.items():
            if any(kw in name_lower for kw in keywords):
                return category

        return "other"

    def _generate_app_description(self, analysis: Dict) -> str:
        """Генерация описания приложения."""
        name = analysis.get("name", "неизвестное")
        version = analysis.get("version", "неизвестно")
        publisher = analysis.get("publisher", "неизвестно")
        category = analysis.get("category", "other")

        category_names = {
            "browser": "веб-браузер",
            "messenger": "мессенджер",
            "editor": "текстовый редактор / IDE",
            "media": "медиа-приложение",
            "game": "игровая платформа",
            "dev": "инструмент разработки",
            "office": "офисное приложение",
            "security": "система безопасности",
            "system": "системная утилита",
            "cloud": "облачное хранилище",
            "other": "приложение"
        }

        cat_name = category_names.get(category, "приложение")

        desc = f"{name} (версия {version}) — это {cat_name} от {publisher}."

        if analysis.get("running"):
            usage = analysis.get("resource_usage", {})
            desc += f" Сейчас запущено. CPU: {usage.get('cpu_percent', 0)}%, RAM: {usage.get('memory_mb', 0)} МБ."

        files = analysis.get("files", {})
        if files.get("total_files"):
            desc += f" Содержит {files['total_files']} файлов ({files.get('total_size_mb', 0)} МБ)."

        return desc

    # === УПРАВЛЕНИЕ ПРИЛОЖЕНИЯМИ ===

    def launch_app(self, app_name: str) -> Dict:
        """Запуск приложения."""
        self.logger.info(f"Запуск приложения: {app_name}")

        # Поиск в базе
        app_id = app_name.lower().replace(" ", "_")
        app_data = self.apps_db.get(app_id)

        if not app_data:
            for key, value in self.apps_db.items():
                if app_name.lower() in key or app_name.lower() in value.get("name", "").lower():
                    app_data = value
                    break

        if not app_data:
            return {"status": "error", "message": f"Приложение '{app_name}' не найдено"}

        # Поиск исполняемого файла
        exe_path = None
        install_path = app_data.get("install_path", "")

        if install_path and Path(install_path).exists():
            # Поиск основного exe
            for exe in Path(install_path).rglob("*.exe"):
                if app_name.lower().split()[0] in exe.stem.lower():
                    exe_path = str(exe)
                    break

            if not exe_path:
                # Берём первый exe
                for exe in Path(install_path).rglob("*.exe"):
                    exe_path = str(exe)
                    break

        if not exe_path:
            return {"status": "error", "message": "Исполняемый файл не найден"}

        try:
            subprocess.Popen([exe_path], shell=True)
            return {
                "status": "ok",
                "message": f"Приложение {app_name} запущено",
                "path": exe_path
            }
        except Exception as e:
            return {"status": "error", "message": f"Ошибка запуска: {e}"}

    def close_app(self, app_name: str) -> Dict:
        """Закрытие приложения."""
        self.logger.info(f"Закрытие приложения: {app_name}")

        closed = []
        app_lower = app_name.lower()

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if app_lower in proc.info["name"].lower():
                    p = psutil.Process(proc.info["pid"])
                    p.terminate()
                    closed.append(proc.info["name"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if closed:
            return {
                "status": "ok",
                "message": f"Закрыто процессов: {len(closed)}",
                "processes": closed
            }

        return {"status": "error", "message": f"Приложение '{app_name}' не запущено"}

    # === ОТЧЁТЫ ===

    def get_full_report(self) -> Dict:
        """Полный отчёт о всех приложениях."""
        if not self.apps_db:
            self.scan_installed_apps()

        categories = {}
        total_size = 0
        running_count = 0

        for app_id, app_data in self.apps_db.items():
            cat = self._categorize_app(app_data.get("name", ""), app_data)
            categories[cat] = categories.get(cat, 0) + 1

            size_kb = app_data.get("size_kb", 0)
            if isinstance(size_kb, (int, float)):
                total_size += size_kb

            if self._is_app_running(app_data.get("name", "")):
                running_count += 1

        return {
            "status": "ok",
            "total_apps": len(self.apps_db),
            "analyzed": sum(1 for a in self.apps_db.values() if a.get("analyzed")),
            "running": running_count,
            "total_size_mb": round(total_size / 1024, 1),
            "categories": categories,
            "top_by_size": self._get_top_apps_by_size()
        }

    def _get_top_apps_by_size(self, limit: int = 10) -> List[Dict]:
        """Топ приложений по размеру."""
        apps_with_size = []

        for app_id, app_data in self.apps_db.items():
            size_kb = app_data.get("size_kb", 0)
            if isinstance(size_kb, (int, float)) and size_kb > 0:
                apps_with_size.append({
                    "name": app_data.get("name", app_id),
                    "size_mb": round(size_kb / 1024, 1),
                    "publisher": app_data.get("publisher", "")
                })

        apps_with_size.sort(key=lambda x: x["size_mb"], reverse=True)
        return apps_with_size[:limit]

    def format_report_message(self, report: Dict) -> str:
        """Форматирование отчёта в сообщение."""
        if report["status"] != "ok":
            return "Не удалось получить отчёт"

        msg = f"📊 Отчёт по приложениям:\n\n"
        msg += f"Всего: {report['total_apps']}\n"
        msg += f"Проанализировано: {report['analyzed']}\n"
        msg += f"Запущено сейчас: {report['running']}\n"
        msg += f"Общий размер: {report['total_size_mb']} МБ\n\n"

        msg += "Категории:\n"
        for cat, count in sorted(report["categories"].items(), key=lambda x: x[1], reverse=True):
            msg += f"  • {cat}: {count}\n"

        if report.get("top_by_size"):
            msg += "\nТоп по размеру:\n"
            for app in report["top_by_size"][:5]:
                msg += f"  • {app['name']} — {app['size_mb']} МБ\n"

        return msg

    def format_analysis_message(self, analysis: Dict) -> str:
        """Форматирование анализа приложения."""
        if analysis.get("status") != "ok":
            return analysis.get("message", "Ошибка анализа")

        a = analysis["analysis"]
        msg = f"📱 Анализ: {a['name']}\n\n"
        msg += f"{a['description']}\n\n"
        msg += f"Версия: {a['version']}\n"
        msg += f"Издатель: {a['publisher']}\n"
        msg += f"Категория: {a['category']}\n"

        if a.get("running"):
            usage = a.get("resource_usage", {})
            msg += f"\n⚡ В запущено:\n"
            msg += f"  CPU: {usage.get('cpu_percent', 0)}%\n"
            msg += f"  RAM: {usage.get('memory_mb', 0)} МБ\n"
            msg += f"  Процессы: {usage.get('process_count', 0)}\n"
        else:
            msg += "\n❌ Не запущено\n"

        files = a.get("files", {})
        if files.get("total_files"):
            msg += f"\n📁 Файлов: {files['total_files']} ({files.get('total_size_mb', 0)} МБ)\n"

        return msg
