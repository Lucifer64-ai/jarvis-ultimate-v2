"""
JARVIS - Окно настроек API подключений
Графический интерфейс для ввода и сохранения API ключей
"""

import os
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    tk = None
    ttk = None
    messagebox = None
    TKINTER_AVAILABLE = False


class SettingsWindow:
    """Окно настроек API подключений."""

    def __init__(self, config_manager):
        self.config = config_manager
        self.root = tk.Tk()
        self.root.title("JARVIS - Настройки API подключений")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Центрируем окно
        self.root.eval('tk::PlaceWindow . center')

        # Стили
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Переменные для полей ввода
        self.entries = {}

        self._create_ui()
        self._load_current_settings()

    def _create_ui(self):
        """Создание интерфейса."""
        # Заголовок
        title_frame = ttk.Frame(self.root, padding="20")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="🔧 JARVIS - Настройки API",
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Введите API ключи для подключения сервисов",
            font=('Arial', 10)
        )
        subtitle_label.pack()

        # Создаём прокручиваемую область
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # === OpenAI ===
        self._create_section(scrollable_frame, "OpenAI (ChatGPT)", [
            ("OPENAI_API_KEY", "API ключ OpenAI", True),
            ("OPENAI_MODEL", "Модель (gpt-4, gpt-3.5-turbo)", False),
        ])

        # === Home Assistant ===
        self._create_section(scrollable_frame, "Home Assistant (Умный дом)", [
            ("HOME_ASSISTANT_URL", "URL сервера (http://192.168.1.100:8123)", False),
            ("HOME_ASSISTANT_TOKEN", "Long-Lived Access Token", True),
        ])

        # === Weather API ===
        self._create_section(scrollable_frame, "OpenWeatherMap (Погода)", [
            ("OPENWEATHER_API_KEY", "API ключ погоды", True),
        ])

        # === News API ===
        self._create_section(scrollable_frame, "NewsAPI (Новости)", [
            ("NEWS_API_KEY", "API ключ новостей", True),
        ])

        # === Mobile API ===
        self._create_section(scrollable_frame, "Мобильное приложение", [
            ("MOBILE_API_SECRET", "Секретный ключ для JWT", True),
            ("MOBILE_API_PORT", "Порт сервера (8080)", False),
        ])

        # === WebSocket ===
        self._create_section(scrollable_frame, "WebSocket сервер", [
            ("WEBSOCKET_PORT", "Порт WebSocket (8765)", False),
        ])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        button_frame = ttk.Frame(self.root, padding="20")
        button_frame.pack(fill=tk.X)

        save_btn = ttk.Button(
            button_frame,
            text="💾 Сохранить",
            command=self._save_settings,
            style='Accent.TButton'
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Отмена",
            command=self.root.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        test_btn = ttk.Button(
            button_frame,
            text="🧪 Тест подключений",
            command=self._test_connections
        )
        test_btn.pack(side=tk.RIGHT, padx=5)

    def _create_section(self, parent, title, fields):
        """Создание секции с полями ввода."""
        section_frame = ttk.LabelFrame(parent, text=title, padding="15")
        section_frame.pack(fill=tk.X, padx=20, pady=10)

        for field_name, label_text, is_secret in fields:
            field_frame = ttk.Frame(section_frame)
            field_frame.pack(fill=tk.X, pady=5)

            # Метка
            label = ttk.Label(field_frame, text=label_text, width=30)
            label.pack(side=tk.LEFT)

            # Поле ввода
            show_char = "*" if is_secret else ""
            entry = ttk.Entry(field_frame, show=show_char, width=35)
            entry.pack(side=tk.LEFT, padx=5)

            self.entries[field_name] = entry

    def _load_current_settings(self):
        """Загрузка текущих настроек из .env файла."""
        env_file = Path('.env')

        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        if key in self.entries and value:
                            self.entries[key].insert(0, value)

    def _save_settings(self):
        """Сохранение настроек в .env файл."""
        # Собираем значения
        settings = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if value:
                settings[key] = value

        # Создаём .env файл
        env_file = Path('.env')

        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("# JARVIS API Configuration\n")
                f.write("# Generated by Settings Window\n\n")

                for key, value in settings.items():
                    f.write(f"{key}={value}\n")

            messagebox.showinfo(
                "Успех",
                "✅ Настройки успешно сохранены!\n\nПерезапустите JARVIS для применения изменений."
            )

            self.root.destroy()

        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"❌ Не удалось сохранить настройки:\n{str(e)}"
            )

    def _test_connections(self):
        """Тестирование подключений к API."""
        messagebox.showinfo(
            "Тест подключений",
            "🧪 Тестирование подключений...\n\n"
            "Эта функция проверит:\n"
            "• OpenAI API\n"
            "• Home Assistant\n"
            "• OpenWeatherMap\n"
            "• NewsAPI\n\n"
            "(Функция в разработке)"
        )

    def show(self):
        """Показать окно."""
        self.root.mainloop()


def show_settings_window(config_manager=None):
    """Функция для показа окна настроек."""
    if not TKINTER_AVAILABLE:
        print("⚠️ tkinter недоступен. Используйте редактирование .env вручную.")
        return None

    if config_manager is None:
        # Создаём простой конфиг-менеджер если не передан
        class SimpleConfig:
            def get_env(self, key, default=None):
                return os.getenv(key, default)

        config_manager = SimpleConfig()

    window = SettingsWindow(config_manager)
    window.show()
    return window


if __name__ == "__main__":
    # Запуск окна настроек
    show_settings_window()
