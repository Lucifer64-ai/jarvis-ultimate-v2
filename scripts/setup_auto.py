"""
JARVIS Auto Setup - Автоматическая установка всех зависимостей
Скачивает и устанавливает всё необходимое для работы JARVIS
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path


class JarvisAutoSetup:
    """Автоматическая установка всех компонентов JARVIS."""

    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_mac = self.system == "darwin"
        self.is_linux = self.system == "linux"

        print("=" * 70)
        print("🤖 JARVIS Ultimate - Автоматическая установка")
        print("=" * 70)
        print(f"Система: {platform.system()} {platform.release()}")
        print(f"Архитектура: {platform.machine()}")
        print(f"Python: {platform.python_version()}")
        print("=" * 70)

    def run_command(self, command: str, shell: bool = True) -> bool:
        """Выполнение команды с выводом."""
        try:
            print(f"\n▶ {command}")
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print(f"✅ Успешно")
                return True
            else:
                print(f"❌ Ошибка: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"❌ Таймаут (5 минут)")
            return False
        except Exception as e:
            print(f"❌ Исключение: {e}")
            return False

    def install_python_dependencies(self) -> bool:
        """Установка Python зависимостей."""
        print("\n" + "=" * 70)
        print("📦 УСТАНОВКА PYTHON ЗАВИСИМОСТЕЙ")
        print("=" * 70)

        # Обновление pip
        print("\n🔄 Обновление pip...")
        if not self.run_command(f"{sys.executable} -m pip install --upgrade pip"):
            print("⚠️  Не удалось обновить pip, продолжаем...")

        # Установка зависимостей
        print("\n📥 Установка зависимостей из requirements.txt...")
        if not self.run_command(f"{sys.executable} -m pip install -r requirements.txt"):
            print("❌ Ошибка установки зависимостей")
            return False

        print("\n✅ Все Python зависимости установлены")
        return True

    def install_ollama(self) -> bool:
        """Установка Ollama для локальной LLM."""
        print("\n" + "=" * 70)
        print("🦙 УСТАНОВКА OLLAMA (Локальная LLM)")
        print("=" * 70)

        # Проверка наличия Ollama
        if self.run_command("ollama --version", shell=True):
            print("✅ Ollama уже установлен")
            return True

        print("\n📥 Ollama не найден, устанавливаем...")

        if self.is_windows:
            # Windows - скачиваем установщик
            print("\n📥 Скачивание Ollama для Windows...")
            url = "https://ollama.com/download/OllamaSetup.exe"
            installer = "OllamaSetup.exe"

            try:
                urllib.request.urlretrieve(url, installer)
                print(f"✅ Скачано: {installer}")

                print("\n🚀 Запуск установщика...")
                print("⚠️  Следуйте инструкциям установщика")
                subprocess.run([installer], shell=True)

                # Удаляем установщик
                os.remove(installer)
                print("✅ Ollama установлен")
                return True

            except Exception as e:
                print(f"❌ Ошибка установки: {e}")
                print("\n💡 Ручная установка:")
                print("   1. Перейдите на https://ollama.com/download")
                print("   2. Скачайте и установите Ollama")
                print("   3. Перезапустите этот скрипт")
                return False

        elif self.is_mac:
            # macOS - используем Homebrew или curl
            print("\n📥 Установка Ollama для macOS...")
            if self.run_command("curl -fsSL https://ollama.com/install.sh | sh"):
                print("✅ Ollama установлен")
                return True
            return False

        elif self.is_linux:
            # Linux - используем curl
            print("\n📥 Установка Ollama для Linux...")
            if self.run_command("curl -fsSL https://ollama.com/install.sh | sh"):
                print("✅ Ollama установлен")
                return True
            return False

        return False

    def download_ollama_model(self, model: str = "llama3.2") -> bool:
        """Скачивание модели для Ollama."""
        print(f"\n📥 Скачивание модели {model}...")

        # Проверяем наличие модели
        result = subprocess.run(
            f"ollama list",
            shell=True,
            capture_output=True,
            text=True
        )

        if model in result.stdout:
            print(f"✅ Модель {model} уже загружена")
            return True

        # Скачиваем модель
        if self.run_command(f"ollama pull {model}"):
            print(f"✅ Модель {model} загружена")
            return True

        print(f"❌ Не удалось загрузить модель {model}")
        return False

    def setup_whisper_models(self) -> bool:
        """Загрузка моделей Whisper."""
        print("\n" + "=" * 70)
        print("🎤 ЗАГРУЗКА МОДЕЛЕЙ WHISPER")
        print("=" * 70)

        try:
            import whisper

            models = ["base", "small"]
            for model in models:
                print(f"\n📥 Загрузка модели Whisper '{model}'...")
                try:
                    whisper.load_model(model)
                    print(f"✅ Модель '{model}' загружена")
                except Exception as e:
                    print(f"⚠️  Ошибка загрузки '{model}': {e}")

            return True
        except ImportError:
            print("❌ Whisper не установлен")
            return False

    def setup_vosk_model(self) -> bool:
        """Загрузка модели Vosk."""
        print("\n" + "=" * 70)
        print("🎤 ЗАГРУЗКА МОДЕЛИ VOSK")
        print("=" * 70)

        models_dir = Path("models/vosk")
        models_dir.mkdir(parents=True, exist_ok=True)

        model_name = "vosk-model-small-ru-0.22"
        model_path = models_dir / model_name

        if model_path.exists():
            print(f"✅ Модель {model_name} уже загружена")
            return True

        print(f"\n📥 Скачивание {model_name}...")
        url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
        zip_path = models_dir / f"{model_name}.zip"

        try:
            urllib.request.urlretrieve(url, zip_path)
            print(f"✅ Скачано: {zip_path}")

            print("\n📦 Распаковка...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(models_dir)

            zip_path.unlink()
            print(f"✅ Модель {model_name} распакована")
            return True

        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return False

    def setup_wake_word(self) -> bool:
        """Настройка wake word."""
        print("\n" + "=" * 70)
        print("🔊 НАСТРОЙКА WAKE WORD")
        print("=" * 70)

        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        config = {
            "enabled": True,
            "wake_word": "джарвис",
            "alternative_words": ["jarvis", "джар"],
            "sensitivity": 0.5,
            "timeout": 2.0,
            "model": "pocketsphinx",
            "language": "ru-RU"
        }

        config_path = config_dir / "wake_word.json"

        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"✅ Конфигурация сохранена: {config_path}")
        print(f"   Wake word: {config['wake_word']}")
        return True

    def check_microphone(self) -> bool:
        """Проверка микрофона."""
        print("\n" + "=" * 70)
        print("🎙️  ПРОВЕРКА МИКРОФОНА")
        print("=" * 70)

        try:
            import speech_recognition as sr

            print("\n🔍 Поиск микрофонов...")
            microphone_list = sr.Microphone.list_microphone_names()

            if not microphone_list:
                print("❌ Микрофоны не найдены")
                return False

            print(f"\n✅ Найдено микрофонов: {len(microphone_list)}")
            for i, name in enumerate(microphone_list[:5]):
                print(f"   {i}: {name}")

            return True
        except Exception as e:
            print(f"❌ Ошибка проверки: {e}")
            return False

    def run_full_setup(self) -> bool:
        """Полная установка всех компонентов."""
        results = {}

        # 1. Python зависимости
        results["python_deps"] = self.install_python_dependencies()

        # 2. Ollama
        results["ollama"] = self.install_ollama()

        # 3. Модель Ollama
        if results["ollama"]:
            results["ollama_model"] = self.download_ollama_model("llama3.2")
        else:
            results["ollama_model"] = False

        # 4. Whisper
        results["whisper"] = self.setup_whisper_models()

        # 5. Vosk
        results["vosk"] = self.setup_vosk_model()

        # 6. Wake word
        results["wake_word"] = self.setup_wake_word()

        # 7. Микрофон
        results["microphone"] = self.check_microphone()

        # Итоги
        print("\n" + "=" * 70)
        print("📊 РЕЗУЛЬТАТЫ УСТАНОВКИ")
        print("=" * 70)

        for component, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {component}")

        success_count = sum(1 for s in results.values() if s)
        total_count = len(results)

        print(f"\nУспешно: {success_count}/{total_count}")

        if success_count >= 5:  # Минимум для базовой работы
            print("\n🎉 JARVIS готов к работе!")
            print("\nЗапуск:")
            print("   python main.py          # Консольный режим")
            print("   python main_hud.py      # HUD интерфейс")
            return True
        else:
            print("\n⚠️  Некоторые компоненты не установлены")
            print("   JARVIS будет работать в ограниченном режиме")
            return False


def main():
    """Основная функция."""
    setup = JarvisAutoSetup()
    success = setup.run_full_setup()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
