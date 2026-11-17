"""
Модуль проактивного ассистента JARVIS (стиль Железного Человека)
- Утренний доклад о состоянии системы
- Напоминания о событиях и задачах
- Системные предупреждения (перегрев, диск, сеть)
- Активные уведомления пользователю
"""

import threading
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ProactiveAssistant:
    """Проактивный ассистент - инициативный помощник в стиле J.A.R.V.I.S."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Конфигурация
        config = brain.config.get("proactive_assistant", {})
        self.enabled = config.get("enabled", True)
        self.morning_report_enabled = config.get("morning_report", True)
        self.system_alerts_enabled = config.get("system_alerts", True)
        self.reminders_enabled = config.get("reminders", True)
        self.morning_hour = config.get("morning_hour", 8)  # 8:00 по умолчанию

        # Состояние
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_morning_report_date: Optional[str] = None

        # Напоминания
        self.reminders: List[Dict] = []
        self.reminders_file = Path("data/reminders.json")
        self.reminders_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_reminders()

        # Системные пороги для предупреждений
        self.alert_thresholds = {
            "cpu_percent": config.get("cpu_threshold", 90),
            "ram_percent": config.get("ram_threshold", 90),
            "disk_percent": config.get("disk_threshold", 90),
            "battery_low": config.get("battery_low", 20),
        }

        # Флаг первого запуска (для утреннего доклада)
        self._first_tick = True

    def _load_reminders(self):
        """Загрузка напоминаний из файла."""
        if self.reminders_file.exists():
            try:
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    self.reminders = json.load(f)
            except Exception as e:
                self.logger.error(f"Ошибка загрузки напоминаний: {e}")
                self.reminders = []

    def _save_reminders(self):
        """Сохранение напоминаний в файл."""
        try:
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения напоминаний: {e}")

    def start(self) -> Dict:
        """Запуск проактивного ассистента."""
        if not self.enabled:
            return {"status": "ok", "message": "Проактивный ассистент отключен в конфиге"}

        if self.running:
            return {"status": "ok", "message": "Уже запущен"}

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Проактивный ассистент запущен")
        return {"status": "ok", "message": "Проактивный ассистент запущен"}

    def stop(self) -> Dict:
        """Остановка проактивного ассистента."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("Проактивный ассистент остановлен")
        return {"status": "ok", "message": "Проактивный ассистент остановлен"}

    def _monitor_loop(self):
        """Основной цикл мониторинга (запускается в отдельном потоке)."""
        while self.running:
            try:
                now = datetime.now()

                # 1. Утренний доклад (один раз в день в указанное время)
                if self.morning_report_enabled:
                    self._check_morning_report(now)

                # 2. Проверка напоминаний
                if self.reminders_enabled:
                    self._check_reminders(now)

                # 3. Системные предупреждения
                if self.system_alerts_enabled:
                    self._check_system_alerts()

            except Exception as e:
                self.logger.error(f"Ошибка в цикле проактивного ассистента: {e}")

            time.sleep(30)  # Проверка каждые 30 секунд

    def _check_morning_report(self, now: datetime):
        """Проверка необходимости утреннего доклада."""
        today_str = now.strftime("%Y-%m-%d")

        # Утренний доклад только один раз в день в указанный час
        if (self.last_morning_report_date == today_str or
                now.hour != self.morning_hour or now.minute > 5):
            return

        # Проверяем, что прошло достаточно времени после запуска
        if self._first_tick:
            self._first_tick = False
            # Не делаем доклад при самом первом тике, подождем следующего цикла
            return

        self.last_morning_report_date = today_str
        self._deliver_morning_report()

    def _deliver_morning_report(self):
        """Доставка утреннего доклада."""
        try:
            now = datetime.now()
            date_str = now.strftime("%d %B %Y")
            weekday = now.strftime("%A")

            # Переводим день недели на русский
            weekdays_ru = {
                "Monday": "понедельник", "Tuesday": "вторник",
                "Wednesday": "среда", "Thursday": "четверг",
                "Friday": "пятница", "Saturday": "суббота", "Sunday": "воскресенье"
            }
            weekday_ru = weekdays_ru.get(weekday, weekday)

            # Собираем информацию
            report_parts = [f"Доброе утро, {self.brain.config.get('voice_personality', {}).get('sir_name', 'Сэр')}."]
            report_parts.append(f"Сегодня {weekday_ru}, {date_str}.")

            # Погода
            if hasattr(self.brain, 'weather_module') and self.brain.weather_module:
                try:
                    weather = self.brain.weather_module.get_weather("Москва")
                    if weather.get("status") == "ok":
                        temp = weather.get("temperature", "?")
                        desc = weather.get("description", "")
                        report_parts.append(f"Погода в Москве: {temp}°C, {desc}.")
                except Exception:
                    pass

            # Курс валют
            if hasattr(self.brain, 'currency_module') and self.brain.currency_module:
                try:
                    rates = self.brain.currency_module.get_rates()
                    if rates.get("status") == "ok":
                        usd = rates.get("usd_rub", "?")
                        eur = rates.get("eur_rub", "?")
                        report_parts.append(f"Курс валют: доллар {usd}, евро {eur} рублей.")
                except Exception:
                    pass

            # Системное состояние
            if PSUTIL_AVAILABLE:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                report_parts.append(f"Состояние системы: загрузка процессора {cpu:.0f}%, оперативной памяти {ram:.0f}%.")

            # Напоминания на сегодня
            today_reminders = [r for r in self.reminders if r.get("date") == now.strftime("%Y-%m-%d")]
            if today_reminders:
                report_parts.append(f"У вас сегодня {len(today_reminders)} напоминаний.")

            report_parts.append("Система готова к работе. Чем могу помочь?")

            full_report = " ".join(report_parts)

            # Говорим через голосовую индивидуальность
            if hasattr(self.brain, 'voice_personality') and self.brain.voice_personality:
                self.brain.voice_personality.speak_professional(full_report)
            elif hasattr(self.brain, 'voice_speaker') and self.brain.voice_speaker:
                self.brain.voice_speaker.speak(full_report)

            self.logger.info("Утренний доклад доставлен")

        except Exception as e:
            self.logger.error(f"Ошибка доставки утреннего доклада: {e}")

    def _check_reminders(self, now: datetime):
        """Проверка и срабатывание напоминаний."""
        now_str = now.strftime("%Y-%m-%d %H:%M")
        now_date = now.strftime("%Y-%m-%d")
        now_time = now.strftime("%H:%M")

        for reminder in self.reminders[:]:  # Копия для безопасного изменения
            if reminder.get("triggered"):
                continue

            reminder_time = reminder.get("time", "")
            reminder_date = reminder.get("date", "")

            # Срабатываем если дата совпадает (или не указана) и время совпадает (с точностью до минуты)
            date_match = (not reminder_date) or (reminder_date == now_date)
            time_match = (not reminder_time) or (reminder_time == now_time)

            if date_match and time_match:
                reminder["triggered"] = True
                self._save_reminders()

                msg = f"Напоминание, {self.brain.config.get('voice_personality', {}).get('sir_name', 'Сэр')}: {reminder.get('text', '')}"
                if hasattr(self.brain, 'voice_personality') and self.brain.voice_personality:
                    self.brain.voice_personality.speak_urgent(msg)
                elif hasattr(self.brain, 'voice_speaker') and self.brain.voice_speaker:
                    self.brain.voice_speaker.speak(msg)

                self.logger.info(f"Напоминание сработало: {reminder.get('text', '')}")

    def _check_system_alerts(self):
        """Проверка системных предупреждений."""
        if not PSUTIL_AVAILABLE:
            return

        try:
            alerts = []

            # CPU
            cpu = psutil.cpu_percent(interval=1)
            if cpu >= self.alert_thresholds["cpu_percent"]:
                alerts.append(f"Внимание! Загрузка процессора превысила {self.alert_thresholds['cpu_percent']}% (сейчас {cpu:.0f}%)")

            # RAM
            ram = psutil.virtual_memory().percent
            if ram >= self.alert_thresholds["ram_percent"]:
                alerts.append(f"Внимание! Использование оперативной памяти превысило {self.alert_thresholds['ram_percent']}% (сейчас {ram:.0f}%)")

            # Диск
            disk = psutil.disk_usage('/').percent
            if disk >= self.alert_thresholds["disk_percent"]:
                alerts.append(f"Внимание! Занято место на диске превысило {self.alert_thresholds['disk_percent']}% (сейчас {disk:.0f}%)")

            # Батарея (если ноутбук)
            try:
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged and battery.percent <= self.alert_thresholds["battery_low"]:
                    alerts.append(f"Внимание! Заряд батареи низкий: {battery.percent}%")
            except Exception:
                pass

            # Оповещаем о критических предупреждениях
            if alerts:
                alert_text = ". ".join(alerts[:3])  # Не более 3 предупреждений за раз
                if hasattr(self.brain, 'voice_personality') and self.brain.voice_personality:
                    self.brain.voice_personality.speak_urgent(alert_text)
                elif hasattr(self.brain, 'voice_speaker') and self.brain.voice_speaker:
                    self.brain.voice_speaker.speak(alert_text)

                self.logger.warning(f"Системные предупреждения: {alert_text}")

        except Exception as e:
            self.logger.error(f"Ошибка проверки системных предупреждений: {e}")

    # === Управление напоминаниями ===

    def add_reminder(self, text: str, date: Optional[str] = None, time: Optional[str] = None) -> Dict:
        """Добавить напоминание."""
        reminder = {
            "id": len(self.reminders) + 1,
            "text": text,
            "date": date,  # Формат YYYY-MM-DD
            "time": time,  # Формат HH:MM
            "triggered": False,
            "created": datetime.now().isoformat()
        }
        self.reminders.append(reminder)
        self._save_reminders()
        self.logger.info(f"Добавлено напоминание: {text}")
        return {"status": "ok", "message": f"Напоминание добавлено: {text}", "reminder": reminder}

    def remove_reminder(self, reminder_id: int) -> Dict:
        """Удалить напоминание по ID."""
        for i, r in enumerate(self.reminders):
            if r.get("id") == reminder_id:
                removed = self.reminders.pop(i)
                self._save_reminders()
                return {"status": "ok", "message": f"Напоминание удалено: {removed.get('text', '')}"}
        return {"status": "error", "message": f"Напоминание с ID {reminder_id} не найдено"}

    def list_reminders(self) -> Dict:
        """Список всех напоминаний."""
        active = [r for r in self.reminders if not r.get("triggered")]
        triggered = [r for r in self.reminders if r.get("triggered")]
        return {
            "status": "ok",
            "active_count": len(active),
            "active": active,
            "triggered_count": len(triggered),
            "total": len(self.reminders)
        }

    def clear_triggered(self) -> Dict:
        """Очистить сработавшие напоминания."""
        count = len([r for r in self.reminders if r.get("triggered")])
        self.reminders = [r for r in self.reminders if not r.get("triggered")]
        self._save_reminders()
        return {"status": "ok", "message": f"Очищено {count} сработавших напоминаний"}

    def get_status(self) -> Dict:
        """Получить статус проактивного ассистента."""
        return {
            "status": "ok",
            "enabled": self.enabled,
            "running": self.running,
            "morning_report": self.morning_report_enabled,
            "system_alerts": self.system_alerts_enabled,
            "reminders": self.reminders_enabled,
            "morning_hour": self.morning_hour,
            "active_reminders": len([r for r in self.reminders if not r.get("triggered")]),
            "thresholds": self.alert_thresholds,
        }
