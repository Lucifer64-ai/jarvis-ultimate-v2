"""
JARVIS - º½¾ ½°¾µº API ¿¾´º»µ½¸¹
°¸µº¸¹ ¸½µµ¹ ´» ²²¾´° ¸ ¾°½µ½¸ API º»µ¹
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path


class SettingsWindow:
    """º½¾ ½°¾µº API ¿¾´º»µ½¸¹."""

    def __init__(self, config_manager):
        self.config = config_manager
        self.root = tk.Tk()
        self.root.title("JARVIS - °¾¹º¸ API ¿¾´º»µ½¸¹")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # ¦µ½¸µ¼ ¾º½¾
        self.root.eval('tk::PlaceWindow . center')

        # ¡¸»¸
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # µµ¼µ½½µ ´» ¿¾»µ¹ ²²¾´°
        self.entries = {}

        self._create_ui()
        self._load_current_settings()

    def _create_ui(self):
        """¡¾·´°½¸µ ¸½µµ¹°."""
        # °³¾»¾²¾º
        title_frame = ttk.Frame(self.root, padding="20")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="¤ JARVIS - °¾¹º¸ API",
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="²µ´¸µ API º»¸ ´» ¿¾´º»µ½¸ µ²¸¾²",
            font=('Arial', 10)
        )
        subtitle_label.pack()

        # ¡¾·´°¼ ¿¾º¸²°µ¼ ¾±»°
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
            ("OPENAI_API_KEY", "API º» OpenAI", True),
            ("OPENAI_MODEL", "¾´µ» (gpt-4, gpt-3.5-turbo)", False),
        ])

        # === Home Assistant ===
        self._create_section(scrollable_frame, "Home Assistant (£¼½¹ ´¾¼)", [
            ("HOME_ASSISTANT_URL", "URL µ²µ° (http://192.168.1.100:8123)", False),
            ("HOME_ASSISTANT_TOKEN", "Long-Lived Access Token", True),
        ])

        # === Weather API ===
        self._create_section(scrollable_frame, "OpenWeatherMap (¾³¾´°)", [
            ("OPENWEATHER_API_KEY", "API º» ¿¾³¾´", True),
        ])

        # === News API ===
        self._create_section(scrollable_frame, "NewsAPI (¾²¾¸)", [
            ("NEWS_API_KEY", "API º» ½¾²¾µ¹", True),
        ])

        # === Mobile API ===
        self._create_section(scrollable_frame, "¾±¸»½¾µ ¿¸»¾¶µ½¸µ", [
            ("MOBILE_API_SECRET", "¡µºµ½¹ º» ´» JWT", True),
            ("MOBILE_API_PORT", "¾ µ²µ° (8080)", False),
        ])

        # === WebSocket ===
        self._create_section(scrollable_frame, "WebSocket µ²µ", [
            ("WEBSOCKET_PORT", "¾ WebSocket (8765)", False),
        ])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ½¾¿º¸ ¿°²»µ½¸
        button_frame = ttk.Frame(self.root, padding="20")
        button_frame.pack(fill=tk.X)

        save_btn = ttk.Button(
            button_frame,
            text="¾ ¡¾°½¸",
            command=self._save_settings,
            style='Accent.TButton'
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(
            button_frame,
            text=" ¼µ½°",
            command=self.root.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        test_btn = ttk.Button(
            button_frame,
            text="§ª ¢µ ¿¾´º»µ½¸¹",
            command=self._test_connections
        )
        test_btn.pack(side=tk.RIGHT, padx=5)

    def _create_section(self, parent, title, fields):
        """¡¾·´°½¸µ µº¸¸  ¿¾»¼¸ ²²¾´°."""
        section_frame = ttk.LabelFrame(parent, text=title, padding="15")
        section_frame.pack(fill=tk.X, padx=20, pady=10)

        for field_name, label_text, is_secret in fields:
            field_frame = ttk.Frame(section_frame)
            field_frame.pack(fill=tk.X, pady=5)

            # µº°
            label = ttk.Label(field_frame, text=label_text, width=30)
            label.pack(side=tk.LEFT)

            # ¾»µ ²²¾´°
            show_char = "*" if is_secret else ""
            entry = ttk.Entry(field_frame, show=show_char, width=35)
            entry.pack(side=tk.LEFT, padx=5)

            self.entries[field_name] = entry

    def _load_current_settings(self):
        """°³·º° µº¸ ½°¾µº ¸· .env °¹»°."""
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
        """¡¾°½µ½¸µ ½°¾µº ² .env °¹»."""
        # ¡¾±¸°µ¼ ·½°µ½¸
        settings = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if value:
                settings[key] = value

        # ¡¾·´°¼ .env °¹»
        env_file = Path('.env')

        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("# JARVIS API Configuration\n")
                f.write("# Generated by Settings Window\n\n")

                for key, value in settings.items():
                    f.write(f"{key}={value}\n")

            messagebox.showinfo(
                "£¿µ",
                " °¾¹º¸ ¿µ½¾ ¾°½µ½!\n\nµµ·°¿¸µ JARVIS ´» ¿¸¼µ½µ½¸ ¸·¼µ½µ½¸¹."
            )

            self.root.destroy()

        except Exception as e:
            messagebox.showerror(
                "¸±º°",
                f" µ ´°»¾ ¾°½¸ ½°¾¹º¸:\n{str(e)}"
            )

    def _test_connections(self):
        """¢µ¸¾²°½¸µ ¿¾´º»µ½¸¹ º API."""
        messagebox.showinfo(
            "¢µ ¿¾´º»µ½¸¹",
            "§ª ¢µ¸¾²°½¸µ ¿¾´º»µ½¸¹...\n\n"
            "­° ½º¸ ¿¾²µ¸:\n"
            "¢ OpenAI API\n"
            "¢ Home Assistant\n"
            "¢ OpenWeatherMap\n"
            "¢ NewsAPI\n\n"
            "(¤½º¸ ² °·°±¾ºµ)"
        )

    def show(self):
        """¾º°·° ¾º½¾."""
        self.root.mainloop()


def show_settings_window(config_manager=None):
    """¤½º¸ ´» ¿¾º°·° ¾º½° ½°¾µº."""
    if config_manager is None:
        # ¡¾·´°¼ ¿¾¾¹ º¾½¸³-¼µ½µ´¶µ µ»¸ ½µ ¿µµ´°½
        class SimpleConfig:
            def get_env(self, key, default=None):
                return os.getenv(key, default)

        config_manager = SimpleConfig()

    window = SettingsWindow(config_manager)
    window.show()


if __name__ == "__main__":
    # °¿º ¾º½° ½°¾µº
    show_settings_window()
