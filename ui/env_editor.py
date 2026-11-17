"""
JARVIS - Окно редактирования файла переменных окружения (.env.example)
Открывает отдельное окно для редактирования конфигурационных ключей
"""

import os
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    tk = None
    ttk = None
    messagebox = None
    filedialog = None
    TKINTER_AVAILABLE = False


class EnvEditorWindow:
    """Окно редактирования файла .env.example."""

    def __init__(self, env_file=".env.example"):
        self.env_file = Path(env_file)
        self.root = tk.Tk()
        self.root.title("JARVIS - Редактор переменных окружения")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Центрируем окно
        self.root.eval('tk::PlaceWindow . center')

        # Цвета в стиле JARVIS (голографический синий)
        self.colors = {
            "bg": "#0a0a1a",
            "fg": "#00ffff",
            "text_bg": "#1a1a3a",
            "text_fg": "#e0e0ff",
            "accent": "#00ffff",
        }

        self.root.configure(bg=self.colors["bg"])

        self._create_ui()
        self._load_file()

    def _create_ui(self):
        """Создание интерфейса."""
        # Заголовок
        title_frame = tk.Frame(self.root, bg=self.colors["bg"], pady=15)
        title_frame.pack(fill=tk.X)

        title_label = tk.Label(
            title_frame,
            text="🔧 JARVIS - Редактор .env.example",
            font=("Courier", 16, "bold"),
            fg=self.colors["accent"],
            bg=self.colors["bg"]
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Редактирование переменных окружения JARVIS",
            font=("Courier", 10),
            fg=self.colors["text_fg"],
            bg=self.colors["bg"]
        )
        subtitle_label.pack()

        # Текстовая область с прокруткой
        text_frame = tk.Frame(self.root, bg=self.colors["text_bg"], padx=10, pady=10)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.text_area = tk.Text(
            text_frame,
            font=("Courier", 11),
            bg=self.colors["text_bg"],
            fg=self.colors["text_fg"],
            insertbackground=self.colors["accent"],
            selectbackground=self.colors["accent"],
            selectforeground=self.colors["bg"],
            wrap=tk.NONE,
            undo=True,
            padx=10,
            pady=10
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = tk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar_y.set)

        scrollbar_x = tk.Scrollbar(self.root, orient="horizontal", command=self.text_area.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.config(xscrollcommand=scrollbar_x.set)

        # Информация о файле
        info_label = tk.Label(
            self.root,
            text=f"Файл: {self.env_file.resolve()}",
            font=("Courier", 9),
            fg="#8888ff",
            bg=self.colors["bg"]
        )
        info_label.pack(anchor="w", padx=20)

        # Кнопки управления
        button_frame = tk.Frame(self.root, bg=self.colors["bg"], pady=15)
        button_frame.pack(fill=tk.X)

        save_btn = tk.Button(
            button_frame,
            text="💾 Сохранить",
            command=self._save_file,
            bg=self.colors["accent"],
            fg=self.colors["bg"],
            font=("Courier", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=20)

        cancel_btn = tk.Button(
            button_frame,
            text="❌ Отмена",
            command=self.root.destroy,
            bg="#444466",
            fg=self.colors["text_fg"],
            font=("Courier", 11),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(
            button_frame,
            text="🔄 Сбросить",
            command=self._reset_file,
            bg="#664400",
            fg=self.colors["text_fg"],
            font=("Courier", 11),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.RIGHT, padx=20)

    def _load_file(self):
        """Загрузка содержимого файла."""
        try:
            if self.env_file.exists():
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "# JARVIS Environment Variables Example\n"
                content += "# Copy this file to .env and fill in your values\n\n"
                content += "# OpenAI API\nOPENAI_API_KEY=your_openai_api_key_here\n"
                content += "OPENAI_MODEL=gpt-4\n\n"
                content += "# OpenWeatherMap\nOPENWEATHER_API_KEY=your_weather_api_key_here\n\n"
                content += "# NewsAPI\nNEWS_API_KEY=your_news_api_key_here\n\n"
                content += "# Mobile API\nMOBILE_API_SECRET=your_secret_here\n"
                content += "MOBILE_API_PORT=8080\n\n"
                content += "# WebSocket\nWEBSOCKET_PORT=8765\n\n"
                content += "# Home Assistant\nHOME_ASSISTANT_URL=http://192.168.1.100:8123\n"
                content += "HOME_ASSISTANT_TOKEN=your_long_lived_token_here\n"

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, content)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def _save_file(self):
        """Сохранение содержимого файла."""
        content = self.text_area.get(1.0, tk.END)

        try:
            # Если это .env.example, предлагаем создать .env
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(content)

            messagebox.showinfo(
                "Успех",
                f"✅ Файл {self.env_file.name} успешно сохранен!\n\n"
                f"Путь: {self.env_file.resolve()}"
            )

        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"❌ Не удалось сохранить файл:\n{str(e)}"
            )

    def _reset_file(self):
        """Сброс содержимого к примеру по умолчанию."""
        if messagebox.askyesno("Сброс", "Сбросить содержимое к примеру по умолчанию?"):
            self._load_file()

    def show(self):
        """Показать окно (блокирующий вызов)."""
        self.root.mainloop()


def open_env_editor(env_file=".env.example"):
    """Открыть окно редактора .env.example."""
    if not TKINTER_AVAILABLE:
        print("⚠️ tkinter недоступен. Используйте текстовый редактор для редактирования .env.example")
        return None

    window = EnvEditorWindow(env_file)
    window.show()
    return window


if __name__ == "__main__":
    open_env_editor()
