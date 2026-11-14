# 🚀 JARVIS Ultimate - Быстрый старт

## 📋 Требования

- Windows 10/11
- Python 3.9+
- Микрофон (для голосового управления)
- Интернет (для загрузки моделей и API)

## ⚡ Быстрая установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/Lucifer64-ai/jarvis-ultimate-v2.git
cd jarvis-ultimate-v2
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

**Основные зависимости:**
- `openai-whisper` - распознавание речи (OpenAI)
- `vosk` - оффлайн распознавание речи
- `torch` - нейросети
- `psutil` - управление процессами
- `scikit-learn` - машинное обучение
- `PyQt5` - графический интерфейс
- `pyautogui` - автоматизация рабочего стола

### 3. Настройка моделей и микрофона

```bash
python scripts/setup_models.py
```

Этот скрипт:
- ✅ Загрузит модели Whisper (base, small, medium)
- ✅ Загрузит модель Vosk для русского языка
- ✅ Настроит wake word "Джарвис"
- ✅ Проверит микрофон

### 4. Запуск JARVIS

```bash
python main.py
```

## 🎤 Голосовое управление

### Wake Word

По умолчанию JARVIS слушает команду **"Джарвис"**.

Альтернативные wake words:
- "Jarvis"
- "Джар"

### Команды

**Системные:**
- "Выключи компьютер"
- "Перезагрузи"
- "Заблокируй экран"
- "Спящий режим"

**Управление рабочим столом:**
- "Сверни все окна"
- "Покажи рабочий стол"
- "Громче" / "Тише"
- "Без звука"

**Приложения:**
- "Открой блокнот"
- "Открой калькулятор"
- "Открой браузер"

**Информация:**
- "Который час?"
- "Какая дата?"
- "Какая погода?"
- "Курс валют"

**Процессы и сеть:**
- "Какие процессы запущены?"
- "Какой мой IP?"
- "Скорость интернета"

## 📁 Структура проекта

```
jarvis-ultimate-v2/
├── main.py                 # Точка входа
├── core/
│   ├── brain.py           # Главный контроллер
│   ├── config.py          # Конфигурация
│   ├── event_bus.py       # Шина событий
│   └── plugin_manager.py  # Менеджер плагинов
├── voice/
│   ├── recognizer.py      # Распознавание речи
│   ├── command_processor.py # Обработка команд
│   └── speaker.py         # Синтез речи
├── modules/
│   ├── process_manager.py # Управление процессами
│   ├── network_manager.py # Управление сетью
│   ├── system.py          # Системные операции
│   ├── desktop_control.py # Управление рабочим столом
│   └── app_launcher.py    # Запуск приложений
├── ai/
│   └── adaptive_ml.py     # ML-движок
├── scripts/
│   └── setup_models.py    # Настройка моделей
└── config/
    └── wake_word.json     # Конфигурация wake word
```

## 🔧 Конфигурация

### Изменение wake word

Отредактируйте `config/wake_word.json`:

```json
{
  "enabled": true,
  "wake_word": "джарвис",
  "alternative_words": ["jarvis", "джар"],
  "sensitivity": 0.5,
  "timeout": 2.0
}
```

### Выбор движка распознавания

В `core/config.py` или через переменные окружения:

```python
voice.engine = "whisper"  # или "vosk", "speechrecognition"
voice.language = "ru-RU"
voice.whisper_model = "base"  # base, small, medium, large
```

## 🐛 Решение проблем

### Микрофон не работает

1. Проверьте подключение микрофона
2. Запустите `python scripts/setup_models.py` для проверки
3. Убедитесь что Python имеет доступ к микрофону (Windows Settings)

### Whisper не загружается

```bash
pip install --upgrade openai-whisper
```

### Vosk не находит модель

Убедитесь что модель загружена в `models/vosk/`:
```bash
python scripts/setup_models.py
```

### Команды не распознаются

1. Говорите чётко и близко к микрофону
2. Попробуйте сменить движок распознавания
3. Проверьте уровень шума в помещении

## 📊 Системные требования

**Минимальные:**
- CPU: 2 ядра
- RAM: 4 GB
- Диск: 2 GB (для моделей)
- Микрофон

**Рекомендуемые:**
- CPU: 4+ ядра
- RAM: 8+ GB
- GPU: NVIDIA с CUDA (для Whisper)
- SSD: 5+ GB

## 🎯 Что работает

✅ **Полностью:**
- Текстовые команды
- Запуск приложений
- Управление рабочим столом
- Системные операции
- Информация о процессах и сети

⚠️ **Требует настройки:**
- Голосовое управление (микрофон + модели)
- Wake word detection
- Погода/новости (API ключи)

❌ **Не реализовано:**
- HUD-интерфейс (стиль Iron Man)
- Полная интеграция с ChatGPT
- Smart Home (Home Assistant)

## 📝 Лицензия

MIT License

## 🤝 Поддержка

GitHub Issues: https://github.com/Lucifer64-ai/jarvis-ultimate-v2/issues
