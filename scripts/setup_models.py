"""
Скрипт загрузки моделей для JARVIS
Whisper и Vosk модели для распознавания речи
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path


def download_file(url: str, dest: str, desc: str = ""):
    """Скачивание файла с прогрессом."""
    print(f"📥 Загрузка {desc or url}...")

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r   Прогресс: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")

    try:
        urllib.request.urlretrieve(url, dest, progress_hook)
        print(f"\n✅ Загружено: {dest}")
        return True
    except Exception as e:
        print(f"\n❌ Ошибка загрузки: {e}")
        return False


def setup_whisper():
    """Загрузка моделей Whisper."""
    print("\n" + "=" * 60)
    print("🎤 НАСТРОЙКА WHISPER")
    print("=" * 60)

    try:
        import whisper
        print("✅ Whisper уже установлен")

        # Загрузка моделей
        models = ["base", "small", "medium"]

        for model_name in models:
            print(f"\n📦 Загрузка модели Whisper '{model_name}'...")
            try:
                model = whisper.load_model(model_name)
                print(f"✅ Модель '{model_name}' загружена")
            except Exception as e:
                print(f"⚠️  Ошибка загрузки модели '{model_name}': {e}")

        return True
    except ImportError:
        print("❌ Whisper не установлен")
        print("   Установите: pip install openai-whisper")
        return False


def setup_vosk():
    """Загрузка моделей Vosk."""
    print("\n" + "=" * 60)
    print("🎤 НАСТРОЙКА VOSK")
    print("=" * 60)

    try:
        from vosk import Model
        print("✅ Vosk уже установлен")
    except ImportError:
        print("❌ Vosk не установлен")
        print("   Установите: pip install vosk")
        return False

    # Создаём папку для моделей
    models_dir = Path("models/vosk")
    models_dir.mkdir(parents=True, exist_ok=True)

    # Модели для загрузки
    vosk_models = {
        "ru": {
            "name": "vosk-model-small-ru-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip",
            "size": "45 MB"
        },
        "ru_large": {
            "name": "vosk-model-ru-0.42",
            "url": "https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip",
            "size": "1.8 GB"
        },
        "en": {
            "name": "vosk-model-small-en-us-0.15",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "size": "40 MB"
        }
    }

    print("\n📦 Доступные модели Vosk:")
    for key, model in vosk_models.items():
        print(f"   • {key}: {model['name']} ({model['size']})")

    # Загружаем русскую маленькую модель по умолчанию
    model_key = "ru"
    model_info = vosk_models[model_key]
    model_path = models_dir / model_info["name"]

    if model_path.exists():
        print(f"\n✅ Модель {model_info['name']} уже загружена")
        return True

    # Скачивание
    zip_path = models_dir / f"{model_info['name']}.zip"

    if download_file(model_info["url"], str(zip_path), model_info["name"]):
        # Распаковка
        print(f"\n📦 Распаковка {model_info['name']}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(models_dir)

            # Удаляем zip
            zip_path.unlink()
            print(f"✅ Модель {model_info['name']} распакована")

            # Проверяем загрузку
            try:
                model = Model(str(model_path))
                print(f"✅ Модель успешно загружается")
                return True
            except Exception as e:
                print(f"⚠️  Ошибка загрузки модели: {e}")
                return False
        except Exception as e:
            print(f"❌ Ошибка распаковки: {e}")
            return False

    return False


def setup_wake_word():
    """Настройка wake word."""
    print("\n" + "=" * 60)
    print("🔊 НАСТРОЙКА WAKE WORD")
    print("=" * 60)

    # Создаём конфигурацию wake word
    config = {
        "enabled": True,
        "wake_word": "джарвис",
        "alternative_words": ["jarvis", "джар"],
        "sensitivity": 0.5,
        "timeout": 2.0,
        "model": "pocketsphinx",
        "language": "ru-RU"
    }

    # Сохраняем конфигурацию
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    import json
    config_path = config_dir / "wake_word.json"

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"✅ Конфигурация wake word сохранена: {config_path}")
    print(f"   Wake word: {config['wake_word']}")
    print(f"   Альтернативы: {', '.join(config['alternative_words'])}")
    print(f"   Чувствительность: {config['sensitivity']}")

    return True


def setup_microphone():
    """Проверка микрофона."""
    print("\n" + "=" * 60)
    print("🎙️  ПРОВЕРКА МИКРОФОНА")
    print("=" * 60)

    try:
        import speech_recognition as sr

        print("🔍 Поиск микрофонов...")
        microphone_list = sr.Microphone.list_microphone_names()

        if not microphone_list:
            print("❌ Микрофоны не найдены")
            return False

        print(f"\n✅ Найдено микрофонов: {len(microphone_list)}")
        for i, name in enumerate(microphone_list):
            print(f"   {i}: {name}")

        # Тест записи
        print("\n🎙️  Тест записи (3 секунды)...")
        print("   Говорите что-нибудь...")

        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)

        print("✅ Запись успешна")

        # Попытка распознавания
        print("\n🔍 Попытка распознавания...")
        try:
            text = recognizer.recognize_google(audio, language="ru-RU")
            print(f"✅ Распознано: {text}")
        except Exception as e:
            print(f"⚠️  Распознавание не удалось: {e}")
            print("   (Это нормально если нет интернета или API недоступен)")

        return True
    except Exception as e:
        print(f"❌ Ошибка проверки микрофона: {e}")
        return False


def main():
    """Основная функция настройки."""
    print("\n" + "=" * 60)
    print("🤖 JARVIS - НАСТРОЙКА МОДЕЛЕЙ И МИКРОФОНА")
    print("=" * 60)

    results = {}

    # 1. Whisper
    results["whisper"] = setup_whisper()

    # 2. Vosk
    results["vosk"] = setup_vosk()

    # 3. Wake Word
    results["wake_word"] = setup_wake_word()

    # 4. Микрофон
    results["microphone"] = setup_microphone()

    # Итоги
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ НАСТРОЙКИ")
    print("=" * 60)

    for component, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {component}")

    success_count = sum(1 for s in results.values() if s)
    total_count = len(results)

    print(f"\nУспешно настроено: {success_count}/{total_count}")

    if success_count == total_count:
        print("\n🎉 Все компоненты настроены! JARVIS готов к работе.")
        print("\nЗапуск: python main.py")
    else:
        print("\n⚠️  Некоторые компоненты не настроены.")
        print("   JARVIS будет работать в текстовом режиме.")

    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
