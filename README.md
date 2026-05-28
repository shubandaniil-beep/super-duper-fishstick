# KinderManager

Облачная система управления детским садом.

## Компоненты

| Компонент | Технология | Хостинг |
|-----------|-----------|---------|
| Backend API | Python FastAPI | Railway (free) |
| Telegram-бот | python-telegram-bot | Railway (тот же сервис) |
| Веб-панель | Next.js 14 | Vercel (free) |
| База данных | PostgreSQL | Supabase (free) |

## Быстрый старт

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # macOS/Linux
pip install -r requirements.txt

# Скопировать и заполнить .env
cp .env.example .env

# Запустить миграции
alembic upgrade head

# Запустить
python main.py
```

### Frontend

```bash
cd frontend
npm install

# Скопировать и заполнить .env.local
cp .env.local.example .env.local

npm run dev
```

## Переменные окружения

### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/kindermanager
SECRET_KEY=ваш_32_символьный_секрет
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
TELEGRAM_BOT_TOKEN=токен_из_BotFather
WEBHOOK_URL=https://ваш-домен.railway.app/webhook
ENVIRONMENT=production
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://ваш-домен.railway.app
```

## Деплой

### Railway (Backend)
1. Создать проект на railway.app
2. Подключить GitHub репо
3. Добавить переменные окружения
4. Railway автодеплоит при push в main

### Vercel (Frontend)
1. Подключить GitHub репо на vercel.com
2. Добавить `NEXT_PUBLIC_API_URL`
3. Автодеплой при push

### Supabase (БД)
1. Создать проект на supabase.com
2. Скопировать Connection String → DATABASE_URL
3. Запустить `alembic upgrade head`

## Первый запуск

После деплоя нужно создать первого суперадмина и садик напрямую в БД:

```sql
-- Создать садик
INSERT INTO kindergartens (id, name, city) 
VALUES (gen_random_uuid(), 'Садик Солнышко', 'Костанай');

-- Создать суперадмина (пароль: bcrypt hash)
INSERT INTO users (id, role, full_name, email, password_hash, is_active)
VALUES (gen_random_uuid(), 'superadmin', 'Daniil', 'admin@example.com', '<bcrypt_hash>', true);
```

## Структура проекта

```
kindermanager/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI роутеры
│   │   ├── bot/          # Telegram-бот
│   │   ├── db/           # Модели + миграции
│   │   ├── services/     # Бизнес-логика
│   │   ├── schemas/      # Pydantic схемы
│   │   └── core/         # Конфиг
│   ├── main.py           # Точка входа
│   └── requirements.txt
└── frontend/
    ├── app/              # Next.js страницы
    ├── components/       # React компоненты
    └── lib/              # Утилиты (api, auth)
```
