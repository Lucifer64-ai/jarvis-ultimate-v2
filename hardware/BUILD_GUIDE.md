# JARVIS Physical Body - Сборка физической части

## 📋 Что это?

Полноценное физическое тело JARVIS как у Тони Старка:
- Голографический дисплей
- Движущаяся "голова" на сервоприводах
- LED индикаторы состояния
- Датчики присутствия и окружающей среды

---

## 🛠 Необходимые компоненты

### 1. Вычислительный блок
- **Raspberry Pi 4** (4GB или 8GB RAM) - мозг JARVIS
- **MicroSD карта** 64GB+ (для ОС)
- **Блок питания** 5V 3A (USB-C)

### 2. Дисплеи
- **Голографический проектор** (опционально, дорого)
- ИЛИ **Прозрачный OLED дисплей** (средний бюджет)
- ИЛИ **Обычный монитор + полупрозрачное зеркало** (бюджетно)

### 3. Движение (сервоприводы)
- **2x Сервопривода** MG996R (для pan/tilt)
- **Коннекторы** для крепления сервоприводов
- **PCA9685** - плата управления сервоприводами (I2C)

### 4. LED индикаторы
- **RGB LED strip** (WS2812B) - 1 метр
- **Arduino Nano** (для управления LED)
- ИЛИ **GPIO Raspberry Pi напрямую** (если LED мало)

### 5. Датчики
- **PIR Motion Sensor** (HC-SR501) - обнаружение движения
- **Ultrasonic Sensor** (HC-SR04) - расстояние до человека
- **DHT22** - температура и влажность
- **Light Sensor** (BH1750) - освещённость

### 6. Звук
- **Микрофон** USB или I2S (ReSpeaker)
- **Динамики** 3.5mm или USB
- ИЛИ **ReSpeaker 4-Mic Array** (для направленного звука)

### 7. Камера (опционально)
- **Raspberry Pi Camera Module** - для распознавания лиц
- ИЛИ **USB веб-камера**

### 8. Корпус
- **3D печатный корпус** (файлы в `/hardware/case/`)
- ИЛИ **Акриловый корпус** из прозрачных боковин

---

## 🔌 Подключение

### Raspberry Pi GPIO

```
Сервоприводы (PCA9685):
- VCC → 5V
- GND → GND
- SDA → GPIO 2 (SDA)
- SCL → GPIO 3 (SCL)

LED Strip (WS2812B):
- VCC → 5V (отдельный блок питания!)
- GND → GND
- DIN → GPIO 18

Датчики:
- PIR Motion → GPIO 22
- Ultrasonic Trig → GPIO 23
- Ultrasonic Echo → GPIO 24
- DHT22 Data → GPIO 17
- Light Sensor (I2C) → SDA/SCL

Микрофон:
- USB микрофон → USB порт
- ИЛИ I2S микрофон → I2S пины
```

---

## 💿 Установка ОС

### 1. Установка Raspberry Pi OS

```bash
# Скачать Raspberry Pi Imager
# Установить Raspberry Pi OS (64-bit)
# Включить SSH и Wi-Fi
```

### 2. Установка зависимостей

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Python и pip
sudo apt install python3-pip python3-venv -y

# GPIO библиотеки
sudo apt install python3-rpi.gpio -y

# Клонирование репозитория
git clone https://github.com/Lucifer64-ai/jarvis-ultimate.git
cd jarvis-ultimate

# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
pip install RPi.GPIO adafruit-circuitpython-pca9685 adafruit-circuitpython-servokit
pip install adafruit-circuitpython-dht adafruit-circuitpython-bh1750
pip install adafruit-circuitpython-neopixel
```

### 3. Настройка конфигурации

Отредактировать `config.json`:

```json
{
  "hardware": {
    "enabled": true,
    "display_type": "projector",
    "display_resolution": "1920x1080",
    "servo_pan_pin": 17,
    "servo_tilt_pin": 27,
    "led_pins": [18, 23, 24],
    "motion_sensor_pin": 22,
    "ultrasonic_trig_pin": 23,
    "ultrasonic_echo_pin": 24,
    "dht_pin": 17
  }
}
```

### 4. Запуск JARVIS

```bash
python main.py
```

---

## 🎮 Использование

### Голосовые команды

**Активация:**
- "Джарвис, включись" - активация hardware
- "Джарвис, выключись" - деактивация

**Движение:**
- "Джарвис, посмотри налево"
- "Джарвис, посмотри направо"
- "Джарвис, смотри на меня"

**LED:**
- "Джарвис, радуга" - радужная анимация
- "Джарвис, дыхание" - плавная пульсация

**Датчики:**
- "Джарвис, температура" - показать температуру
- "Джарвис, кто-нибудь есть?" - проверка присутствия
- "Джарвис, статус среды" - все показания датчиков

---

## 📦 Сборка корпуса

### Вариант 1: 3D печать

Файлы для 3D печати находятся в `/hardware/case/`:
- `head.stl` - голова JARVIS
- `base.stl` - основание
- `mount.stl` - крепление для Raspberry Pi

**Материал:** PLA или PETG
**Цвет:** Серебристый или белый

### Вариант 2: Акриловый корпус

Использовать лазерную резку акрила по чертежам из `/hardware/case/dxf/`.

---

## 🔧 Troubleshooting

### Сервоприводы не двигаются
- Проверить подключение PCA9685 (I2C)
- Убедиться, что питание 5V подаётся на PCA9685
- Проверить адрес I2C: `sudo i2cdetect -y 1`

### LED не светятся
- Проверить подключение DIN к GPIO 18
- Убедиться, что используется отдельный блок питания для LED strip
- Проверить количество LED в коде

### Датчики не работают
- PIR: проверить подключение к GPIO 22
- Ultrasonic: проверить Trig (GPIO 23) и Echo (GPIO 24)
- DHT22: проверить подключение Data к GPIO 17

### Микрофон не слышит
- Проверить `arecord -l` - список микрофонов
- Настроить default microphone в `/etc/asound.conf`

---

## 💰 Бюджеты

### Минимальный (бюджетный) - ~$150
- Raspberry Pi 4 (4GB) - $55
- Обычный монитор (б/у) - $30
- 2x сервопривода - $15
- LED strip - $10
- Датчики - $20
- Микрофон + динамики - $20

### Средний - ~$300
- Raspberry Pi 4 (8GB) - $75
- Прозрачный OLED дисплей - $100
- PCA9685 + сервоприводы - $30
- ReSpeaker 2-Mic - $25
- Все датчики - $30
- 3D печатный корпус - $40

### Премиум (как у Тони Старка) - ~$1000+
- Голографический проектор - $500+
- Raspberry Pi Cluster - $200
- ReSpeaker 4-Mic Array - $100
- Премиум сервоприводы - $100
- Автоматный корпус - $100+

---

## 🚀 Следующие шаги

1. **Заказать компоненты** с AliExpress/Amazon
2. **Собрать hardware** по схеме подключения
3. **Напечатать корпус** (опционально)
4. **Установить ОС** на Raspberry Pi
5. **Настроить конфигурацию**
6. **Запустить JARVIS** и наслаждаться!

---

## 📞 Поддержка

Если возникли вопросы:
- GitHub Issues: https://github.com/Lucifer64-ai/jarvis-ultimate/issues
- Документация: https://github.com/Lucifer64-ai/jarvis-ultimate/wiki

---

**Создано для тех, кто хочет создать настоящего JARVIS, а не просто программу на рабочем столе.**

*"Sometimes you gotta run before you can walk." - Tony Stark*
