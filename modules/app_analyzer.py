"""
App Analyzer Module - ½°»¸· °½¾²»µ½½ ¿¸»¾¶µ½¸¹ ½° 
JARVIS º°½¸µ, ¸·°µ ¸ °·±¸°µ ² ¿¸»¾¶µ½¸
"""

import os
import json
import subprocess
import winreg
import psutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class AppAnalyzer:
    """¾´» °½°»¸·° ¿¸»¾¶µ½¸¹ ½° ."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger
        self.config = brain.config
        
        # °·° ´°½½ ¿¸»¾¶µ½¸¹
        self.apps_db = {}
        self.db_path = Path("data/apps_database.json")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # °³·º° µ²µ¹ 
        self._load_database()
        
        # ¸ ´» º°½¸¾²°½¸
        self.scan_paths = [
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")),
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")),
            Path(os.environ.get("LOCALAPPDATA", "")),
            Path(os.environ.get("APPDATA", "")),
            Path(os.path.expanduser("~\\Desktop")),
            Path(os.environ.get("USERPROFILE", "")),
        ]
        
        #  °¸µ½¸ ¸¿¾»½µ¼ °¹»¾²
        self.executable_extensions = {".exe", ".msi", ".bat", ".cmd", ".ps1", ".com"}
        
        #  °¸µ½¸ ´¾º¼µ½¾² ´» °½°»¸·°
        self.document_extensions = {
            ".txt", ".md", ".json", ".xml", ".yaml", ".yml",
            ".ini", ".cfg", ".conf", ".log",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx",
            ".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h"
        }
        
        self.logger.info("¢ ¾´» °½°»¸·° ¿¸»¾¶µ½¸¹ ¸½¸¸°»¸·¸¾²°½")

    def _load_database(self):
        """°³·º° ±°· ´°½½ ¿¸»¾¶µ½¸¹."""
        try:
            if self.db_path.exists():
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.apps_db = json.load(f)
                self.logger.info(f"°³¶µ½°  ¿¸»¾¶µ½¸¹: {len(self.apps_db)} ·°¿¸µ¹")
            else:
                self.apps_db = {}
        except Exception as e:
            self.logger.error(f"¸±º° ·°³·º¸ : {e}")
            self.apps_db = {}

    def _save_database(self):
        """¡¾°½µ½¸µ ±°· ´°½½ ¿¸»¾¶µ½¸¹."""
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.apps_db, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"¸±º° ¾°½µ½¸ : {e}")

    # === ¡  ===

    def scan_installed_apps(self) -> Dict:
        """¡º°½¸¾²°½¸µ °½¾²»µ½½ ¿¸»¾¶µ½¸¹ µµ· µµ Windows."""
        self.logger.info("¡º°½¸¾²°½¸µ °½¾²»µ½½ ¿¸»¾¶µ½¸¹...")
        apps = []
        
        # »¸ µµ° ´» ¿¾¸º°
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
                self.logger.debug(f"¸±º° µ½¸ µµ° {path}: {e}")
        
        # ±½¾²»µ½¸µ 
        for app in apps:
            app_id = app.get("name", "").lower().replace(" ", "_")
            self.apps_db[app_id] = {
                **app,
                "last_seen": datetime.now().isoformat(),
                "analyzed": self.apps_db.get(app_id, {}).get("analyzed", False)
            }
        
        self._save_database()
        
        self.logger.info(f"°¹´µ½¾ {len(apps)} °½¾²»µ½½ ¿¸»¾¶µ½¸¹")
        return {
            "status": "ok",
            "count": len(apps),
            "apps": apps
        }

    def _read_registry_app(self, key) -> Optional[Dict]:
        """§µ½¸µ ¸½¾¼°¸¸ ¾ ¿¸»¾¶µ½¸¸ ¸· µµ°."""
        try:
            name = winreg.QueryValueEx(key, "DisplayName")[0]
        except (OSError, FileNotFoundError):
            return None
        
        app_info = {"name": name}
        
        # ¾¿¾»½¸µ»½µ ¿¾»
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
        """¡º°½¸¾²°½¸µ ¸¿¾»½µ¼ °¹»¾² ² ´¸µº¾¸."""
        self.logger.info("¡º°½¸¾²°½¸µ ¸¿¾»½µ¼ °¹»¾²...")
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
                self.logger.debug(f"¸±º° º°½¸¾²°½¸ {scan_path}: {e}")
        
        return {
            "status": "ok",
            "count": len(executables),
            "executables": executables[:100]  # ³°½¸µ½¸µ
        }

    def _analyze_executable(self, path: Path) -> Optional[Dict]:
        """½°»¸· ¸¿¾»½µ¼¾³¾ °¹»°."""
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
            
            # µ¸ °¹»° (Windows)
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
            self.logger.debug(f"¸±º° °½°»¸·° {path}: {e}")
            return None

    # ===   ¯ ===

    def analyze_app(self, app_name: str) -> Dict:
        """»±¾º¸¹ °½°»¸· º¾½ºµ½¾³¾ ¿¸»¾¶µ½¸."""
        self.logger.info(f"½°»¸· ¿¸»¾¶µ½¸: {app_name}")
        
        app_id = app_name.lower().replace(" ", "_")
        
        # ¾¸º ² 
        app_data = self.apps_db.get(app_id)
        if not app_data:
            # ¾¸º ¿¾ °¸½¾¼ ¾²¿°´µ½¸
            for key, value in self.apps_db.items():
                if app_name.lower() in key or app_name.lower() in value.get("name", "").lower():
                    app_data = value
                    app_id = key
                    break
        
        if not app_data:
            return {"status": "error", "message": f"¸»¾¶µ½¸µ '{app_name}' ½µ ½°¹´µ½¾"}
        
        # »±¾º¸¹ °½°»¸·
        analysis = {
            "name": app_data.get("name", app_name),
            "version": app_data.get("version", "½µ¸·²µ½¾"),
            "publisher": app_data.get("publisher", "½µ¸·²µ½¾"),
            "install_path": app_data.get("install_path", ""),
            "size_kb": app_data.get("size_kb", 0),
            "install_date": app_data.get("install_date", "½µ¸·²µ½¾"),
        }
        
        # ½°»¸· °¹»¾² ¿¸»¾¶µ½¸
        if analysis["install_path"] and Path(analysis["install_path"]).exists():
            analysis["files"] = self._analyze_app_files(Path(analysis["install_path"]))
        
        # ½°»¸· ¿¾µ¾²
        analysis["running"] = self._is_app_running(app_name)
        if analysis["running"]:
            analysis["processes"] = self._get_app_processes(app_name)
        
        # ½°»¸· µ¾²
        if analysis["running"] and analysis.get("processes"):
            analysis["resource_usage"] = self._get_app_resource_usage(analysis["processes"])
        
        # °µ³¾¸·°¸
        analysis["category"] = self._categorize_app(app_name, app_data)
        
        # ¿¸°½¸µ
        analysis["description"] = self._generate_app_description(analysis)
        
        # ±½¾²»µ½¸µ 
        self.apps_db[app_id] = {
            **app_data,
            "analyzed": True,
            "last_analyzed": datetime.now().isoformat(),
            "analysis": analysis
        }
        self._save_database()
        
        return {"status": "ok", "analysis": analysis}

    def _analyze_app_files(self, app_path: Path) -> Dict:
        """½°»¸· °¹»¾² ¿¸»¾¶µ½¸."""
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
            self.logger.debug(f"¸±º° °½°»¸·° °¹»¾² {app_path}: {e}")
        
        files_info["total_size_mb"] = round(files_info["total_size_mb"], 2)
        return files_info

    def _is_app_running(self, app_name: str) -> bool:
        """¾²µº°, ·°¿µ½¾ »¸ ¿¸»¾¶µ½¸µ."""
        app_lower = app_name.lower()
        for proc in psutil.process_iter(["name"]):
            try:
                if app_lower in proc.info["name"].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def _get_app_processes(self, app_name: str) -> List[Dict]:
        """¾»µ½¸µ ¸½¾¼°¸¸ ¾ ¿¾µ° ¿¸»¾¶µ½¸."""
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
        """¾»µ½¸µ ¸¿¾»·¾²°½¸ µ¾² ¿¸»¾¶µ½¸µ¼."""
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
        """°µ³¾¸·°¸ ¿¸»¾¶µ½¸."""
        name_lower = app_name.lower()
        
        categories = {
            "browser": ["chrome", "firefox", "edge", "opera", "brave", "safari", "½´µº"],
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
        """µ½µ°¸ ¾¿¸°½¸ ¿¸»¾¶µ½¸."""
        name = analysis.get("name", "µ¸·²µ½¾µ")
        version = analysis.get("version", "½µ¸·²µ½¾")
        publisher = analysis.get("publisher", "½µ¸·²µ½¾")
        category = analysis.get("category", "other")
        
        category_names = {
            "browser": "²µ±-±°·µ",
            "messenger": "¼µµ½´¶µ",
            "editor": "µº¾²¹ µ´°º¾ / IDE",
            "media": "¼µ´¸°-¿¸»¾¶µ½¸µ",
            "game": "¸³¾²° ¿»°¾¼°",
            "dev": "¸½¼µ½ °·°±¾º¸",
            "office": "¾¸½¾µ ¿¸»¾¶µ½¸µ",
            "security": "¸µ¼° ±µ·¾¿°½¾¸",
            "system": "¸µ¼½° ¸»¸°",
            "cloud": "¾±»°½¾µ °½¸»¸µ",
            "other": "¿¸»¾¶µ½¸µ"
        }
        
        cat_name = category_names.get(category, "¿¸»¾¶µ½¸µ")
        
        desc = f"{name} (²µ¸ {version}) ¢ ¾ {cat_name} ¾ {publisher}."
        
        if analysis.get("running"):
            usage = analysis.get("resource_usage", {})
            desc += f" ¡µ¹° ·°¿µ½¾. CPU: {usage.get('cpu_percent', 0)}%, RAM: {usage.get('memory_mb', 0)} ."
        
        files = analysis.get("files", {})
        if files.get("total_files"):
            desc += f" ¡¾´µ¶¸ {files['total_files']} °¹»¾² ({files.get('total_size_mb', 0)} )."
        
        return desc

    # === £   ¯ ===

    def launch_app(self, app_name: str) -> Dict:
        """°¿º ¿¸»¾¶µ½¸."""
        self.logger.info(f"°¿º ¿¸»¾¶µ½¸: {app_name}")
        
        # ¾¸º ² 
        app_id = app_name.lower().replace(" ", "_")
        app_data = self.apps_db.get(app_id)
        
        if not app_data:
            for key, value in self.apps_db.items():
                if app_name.lower() in key or app_name.lower() in value.get("name", "").lower():
                    app_data = value
                    break
        
        if not app_data:
            return {"status": "error", "message": f"¸»¾¶µ½¸µ '{app_name}' ½µ ½°¹´µ½¾"}
        
        # ¾¸º ¸¿¾»½µ¼¾³¾ °¹»°
        exe_path = None
        install_path = app_data.get("install_path", "")
        
        if install_path and Path(install_path).exists():
            # ¾¸º ¾½¾²½¾³¾ exe
            for exe in Path(install_path).rglob("*.exe"):
                if app_name.lower().split()[0] in exe.stem.lower():
                    exe_path = str(exe)
                    break
            
            if not exe_path:
                # µ¼ ¿µ²¹ exe
                for exe in Path(install_path).rglob("*.exe"):
                    exe_path = str(exe)
                    break
        
        if not exe_path:
            return {"status": "error", "message": "¿¾»½µ¼¹ °¹» ½µ ½°¹´µ½"}
        
        try:
            subprocess.Popen([exe_path], shell=True)
            return {
                "status": "ok",
                "message": f"¸»¾¶µ½¸µ {app_name} ·°¿µ½¾",
                "path": exe_path
            }
        except Exception as e:
            return {"status": "error", "message": f"¸±º° ·°¿º°: {e}"}

    def close_app(self, app_name: str) -> Dict:
        """°º¸µ ¿¸»¾¶µ½¸."""
        self.logger.info(f"°º¸µ ¿¸»¾¶µ½¸: {app_name}")
        
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
                "message": f"°º¾ ¿¾µ¾²: {len(closed)}",
                "processes": closed
            }
        
        return {"status": "error", "message": f"¸»¾¶µ½¸µ '{app_name}' ½µ ·°¿µ½¾"}

    # === ¢§¢« ===

    def get_full_report(self) -> Dict:
        """¾»½¹ ¾ ¾ ²µ ¿¸»¾¶µ½¸."""
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
        """¢¾¿ ¿¸»¾¶µ½¸¹ ¿¾ °·¼µ."""
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
        """¤¾¼°¸¾²°½¸µ ¾° ² ¾¾±µ½¸µ."""
        if report["status"] != "ok":
            return "µ ´°»¾ ¿¾»¸ ¾"
        
        msg = f"°  ¿¾ ¿¸»¾¶µ½¸¼:\n\n"
        msg += f"µ³¾: {report['total_apps']}\n"
        msg += f"¾°½°»¸·¸¾²°½¾: {report['analyzed']}\n"
        msg += f"°¿µ½¾ µ¹°: {report['running']}\n"
        msg += f"±¸¹ °·¼µ: {report['total_size_mb']} \n\n"
        
        msg += "°µ³¾¸¸:\n"
        for cat, count in sorted(report["categories"].items(), key=lambda x: x[1], reverse=True):
            msg += f"  ¢¢ {cat}: {count}\n"
        
        if report.get("top_by_size"):
            msg += "\n¢¾¿ ¿¾ °·¼µ:\n"
            for app in report["top_by_size"][:5]:
                msg += f"  ¢¢ {app['name']} ¢ {app['size_mb']} \n"
        
        return msg

    def format_analysis_message(self, analysis: Dict) -> str:
        """¤¾¼°¸¾²°½¸µ °½°»¸·° ¿¸»¾¶µ½¸."""
        if analysis.get("status") != "ok":
            return analysis.get("message", "¸±º° °½°»¸·°")
        
        a = analysis["analysis"]
        msg = f"° ½°»¸·: {a['name']}\n\n"
        msg += f"{a['description']}\n\n"
        msg += f"µ¸: {a['version']}\n"
        msg += f"·´°µ»: {a['publisher']}\n"
        msg += f"°µ³¾¸: {a['category']}\n"
        
        if a.get("running"):
            usage = a.get("resource_usage", {})
            msg += f"\n¢¡ °¿µ½¾:\n"
            msg += f"  CPU: {usage.get('cpu_percent', 0)}%\n"
            msg += f"  RAM: {usage.get('memory_mb', 0)} \n"
            msg += f"  ¾µ: {usage.get('process_count', 0)}\n"
        else:
            msg += "\n¢¸ µ ·°¿µ½¾\n"
        
        files = a.get("files", {})
        if files.get("total_files"):
            msg += f"\n° ¤°¹»: {files['total_files']} ({files.get('total_size_mb', 0)} )\n"
        
        return msg
