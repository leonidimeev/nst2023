# nst2023

## Как запустить

### Ручной запуск
1. pip install --no-cache-dir -r requirements.txt
2. запустить postgre
3. Настроить в переменной окружения: 
BOT_TOKEN - токен телеграм бота
OPENAI_API_KEY - токен open ai аккаунта
DATABASE_USER - пользователь базы данных postgres
DATABASE_PASSWORD - пароль базы данных postgres
4. запустить bot.py

### Docker
1. Добавить в .env: 
BOT_TOKEN - токен телеграм бота
OPENAI_API_KEY - токен open ai аккаунта
2. docker-compose up