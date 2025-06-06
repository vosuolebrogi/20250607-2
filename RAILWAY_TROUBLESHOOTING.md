# Railway Deployment Troubleshooting Guide

## Проблема: "1/1 replicas never became healthy!"

### Исправления (уже внесены в код):

1. **✅ Упростили health server**
   - Убрали сложную классовую структуру
   - Используем простые async функции
   - Исправили asyncio integration

2. **✅ Обновили railway.json**
   - Убрали `healthcheckPath` который мог вызывать проблемы
   - Оставили только базовую конфигурацию

3. **✅ Исправили Dockerfile**
   - Убрали создание non-root пользователя
   - Исправили EXPOSE директиву для Railway
   - Упростили конфигурацию

4. **✅ Исправили запуск приложения**
   - Health server запускается в background task
   - Бот и сервер работают параллельно
   - Добавлена задержка для инициализации

### Дополнительные шаги для устранения неполадок:

#### 1. Проверьте переменные окружения в Railway
```
TELEGRAM_BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
PORT=8000  # (Railway может установить автоматически)
```

#### 2. Проверьте логи Railway
- Откройте ваш проект в Railway
- Перейдите в раздел "Deployments"
- Просмотрите логи последнего развертывания

#### 3. Если проблема повторяется:

**Опция A: Запуск без health server**
```python
# В bot.py закомментируйте эти строки:
# health_task = asyncio.create_task(start_health_server(port))
# await asyncio.sleep(2)
```

**Опция B: Альтернативный Dockerfile**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-u", "bot.py"]
```

#### 4. Проверка локально с Docker:
```bash
# Сборка образа
docker build -t location-bot .

# Тест локально
docker run --env-file .env -p 8000:8000 location-bot
```

#### 5. Минимальный тест health endpoint:
```bash
# После развертывания проверьте:
curl https://your-railway-app.railway.app/health
# Должен вернуть: {"status": "healthy", "service": "location-facts-bot"}
```

### Альтернативные решения:

#### 1. Используйте web.py вместо health_server.py:
```python
from aiohttp import web
import os

async def health(request):
    return web.json_response({"status": "ok"})

app = web.Application()
app.router.add_get('/health', health)

if __name__ == '__main__':
    web.run_app(app, port=int(os.getenv('PORT', 8000)))
```

#### 2. Используйте gunicorn для production:
```bash
# requirements.txt
gunicorn==21.2.0

# Procfile или railway.json
"startCommand": "gunicorn --bind 0.0.0.0:$PORT bot:app"
```

### Статус исправлений:
- ✅ Health server упрощен
- ✅ Railway.json обновлен  
- ✅ Dockerfile исправлен
- ✅ Asyncio integration исправлен
- ✅ Код загружен в репозиторий

Railway должен успешно развернуть приложение после этих исправлений. 