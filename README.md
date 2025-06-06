# 🌍 Location Facts Telegram Bot

Telegram-бот для получения интересных фактов о местах рядом с вашим местоположением. Использует OpenAI GPT-4o-mini для генерации увлекательных фактов о ближайших достопримечательностях.

## 🚀 Возможности

- 📍 Принимает геолокацию от пользователя
- 🤖 Использует GPT-4o-mini для поиска интересных фактов
- 🌟 Генерирует необычные и малоизвестные факты о местах
- 🔄 Поддержка живой локации (версия 1.1)

## 🛠️ Установка и настройка

### Предварительные требования

- Python 3.12+
- Telegram Bot Token (получить у @BotFather)
- OpenAI API Key

### Локальная установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd location-facts-bot
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения:**
   
   Создайте файл `.env` в корне проекта:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Запустите бота:**
   ```bash
   python main.py
   ```

### Запуск с Docker

1. **Соберите образ:**
   ```bash
   docker build -t location-facts-bot .
   ```

2. **Запустите контейнер:**
   ```bash
   docker run -d --name location-bot \
     -e TELEGRAM_BOT_TOKEN=your_token \
     -e OPENAI_API_KEY=your_api_key \
     location-facts-bot
   ```

## 📖 Использование

1. Найдите бота в Telegram по имени пользователя
2. Нажмите `/start` для начала работы
3. Отправьте свою геолокацию через меню вложений (📎 → Местоположение)
4. Получите интересный факт о ближайшем месте!

### Команды бота

- `/start` - начать работу с ботом
- `/help` - показать справку по использованию

## 🚀 Развертывание на Railway

1. Создайте новый проект на [Railway](https://railway.app)
2. Подключите свой GitHub репозиторий
3. Добавьте переменные окружения:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
4. Railway автоматически соберет и запустит ваш бот

## 📋 Планы развития

### Версия 1.1
- ✅ Базовая функциональность с геолокацией
- 🔄 Поддержка живой локации
- ⏰ Обновление фактов каждые 10 минут при движении
- 📊 Расширенная аналитика и логирование

## 🤝 Разработка

### Структура проекта

```
location-facts-bot/
├── main.py              # Основной файл бота
├── requirements.txt     # Python зависимости
├── Dockerfile          # Docker конфигурация
├── .dockerignore       # Docker ignore правила
├── .gitignore          # Git ignore правила
├── README.md           # Документация
└── docs/               # Дополнительная документация
    ├── prd.md         # Product Requirements Document
    └── implementation_plan.mdc  # План реализации
```

### Технологический стек

- **Python 3.12** - основной язык программирования
- **python-telegram-bot 20.8** - Telegram Bot API
- **OpenAI API** - генерация фактов о местах
- **Docker** - контейнеризация
- **Railway** - хостинг и развертывание

## 📄 Лицензия

MIT License

## 🐛 Сообщить об ошибке

Создайте issue в GitHub репозитории с описанием проблемы. 