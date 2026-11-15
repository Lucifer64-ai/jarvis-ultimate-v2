# 📱 JARVIS Mobile App

Мобильное приложение для управления JARVIS Ultimate с телефона.

## 🚀 Возможности

- 🎤 **Голосовое управление** - отдавайте команды голосом
- 💬 **Текстовые команды** - вводите команды текстом
- 📊 **Мониторинг системы** - CPU, RAM, сеть в реальном времени
- 📝 **Лог команд** - история всех команд и ответов
- ⚙️ **Настройки** - выбор LLM режима, IP сервера
- 🔄 **WebSocket** - мгновенная связь с JARVIS

## 📦 Установка

### Требования
- Node.js 18+
- React Native CLI
- Android Studio (для Android)
- Xcode (для iOS, только macOS)

### Шаги установки

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/Lucifer64-ai/jarvis-ultimate-v2.git
cd jarvis-ultimate-v2/mobile-app
```

2. **Установите зависимости**
```bash
npm install
```

3. **Запустите приложение**

**Android:**
```bash
npm run android
```

**iOS (только macOS):**
```bash
npm run ios
```

## 🔧 Настройка

1. Откройте приложение
2. Перейдите в **Настройки**
3. Укажите IP адрес вашего компьютера с JARVIS
4. Убедитесь что JARVIS запущен на ПК

## 📱 Скриншоты

- **Главный экран** - голосовое управление и быстрые команды
- **Статус** - мониторинг системы в реальном времени
- **Лог** - история команд и ответов
- **Настройки** - конфигурация подключения и LLM

## 🛠️ Технологии

- React Native 0.73
- React Navigation
- WebSocket
- AsyncStorage
- react-native-voice

## 📂 Структура

```
mobile-app/
├── App.js                 # Главный компонент
├── package.json           # Зависимости
├── src/
│   ├── screens/          # Экраны приложения
│   │   ├── HomeScreen.js
│   │   ├── StatusScreen.js
│   │   ├── SettingsScreen.js
│   │   └── LogScreen.js
│   └── services/         # Сервисы
│       └── websocket.js  # WebSocket клиент
```

## 🔌 WebSocket API

Приложение общается с JARVIS через WebSocket:

**Команды от приложения:**
```json
{ "type": "command", "text": "который час?" }
{ "type": "get_status" }
{ "type": "get_logs" }
{ "type": "clear_logs" }
```

**Ответы от JARVIS:**
```json
{ "type": "response", "message": "Сейчас 15:30" }
{ "type": "status", "data": { "cpu": 45, "ram": 60 } }
{ "type": "logs_history", "logs": [...] }
```

## 🐛 Решение проблем

**Не подключается к JARVIS:**
- Убедитесь что JARVIS запущен на ПК
- Проверьте IP адрес в настройках
- Убедитесь что оба устройства в одной сети

**Голосовое управление не работает:**
- Проверьте разрешения микрофона
- Убедитесь что интернет подключен (для Google Speech API)

## 📝 Лицензия

MIT License
