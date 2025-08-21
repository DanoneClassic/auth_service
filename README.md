# Authentication Service

Сервис авторизации с чистой архитектурой на Python 3.12, FastAPI, PostgreSQL и Docker.

## Архитектура

Проект построен на принципах чистой архитектуры с разделением на слои:

- **API Layer** (`app/api/`) - FastAPI endpoints
- **Service Layer** (`app/services/`) - бизнес-логика
- **Repository Layer** (`app/repositories/`) - работа с БД
- **Domain Layer** (`app/models/`) - модели и схемы

## Функциональность

- ✅ Регистрация пользователей
- ✅ Авторизация по email/паролю
- ✅ JWT токены (access + refresh)
- ✅ Защищенные эндпоинты
- ✅ Обновление токенов
- ✅ Хеширование паролей (bcrypt)
- ✅ Валидация данных (Pydantic)
- ✅ Async/await поддержка
- ✅ Docker контейнеризация
- ✅ Database миграции (Alembic)
- ✅ Health checks
- ✅ CORS middleware
- ✅ Request ID tracking

## Быстрый запуск

### С Docker Compose (рекомендуется)

```bash
# Клонировать и перейти в папку
cd auth_service

# Запустить все сервисы
docker-compose up -d

# Проверить здоровье сервиса
curl http://localhost:8000/health
```

### Локальная разработка

```bash
# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env под свои настройки

# Запустить PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_DB=auth_db \
  -e POSTGRES_USER=auth_user \
  -e POSTGRES_PASSWORD=auth_password \
  -p 5432:5432 postgres:15-alpine

# Выполнить миграции
alembic upgrade head

# Запустить сервис
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

### Авторизация
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Получение профиля пользователя
```bash
# Заменить YOUR_ACCESS_TOKEN на реальный токен
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Обновление токена
```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### Health check
```bash
curl http://localhost:8000/health
```

## Структура проекта

```
auth_service/
├── app/                     # Основное приложение
│   ├── api/                 # API эндпоинты
│   │   └── auth.py         # Авторизационные роуты
│   ├── models/             # Модели данных
│   │   ├── user.py         # SQLAlchemy модель User
│   │   └── schemas.py      # Pydantic схемы
│   ├── repositories/       # Слой доступа к данным
│   │   └── user_repository.py
│   ├── services/           # Бизнес-логика
│   │   └── auth_service.py
│   ├── utils/              # Утилиты
│   │   ├── security.py     # JWT, хеширование
│   │   └── exceptions.py   # Кастомные исключения
│   ├── config.py           # Настройки приложения
│   ├── database.py         # Подключение к БД
│   ├── dependencies.py     # FastAPI зависимости
│   └── main.py             # Главный файл приложения
├── alembic/                # Миграции БД
├── requirements.txt        # Python зависимости
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Оркестрация контейнеров
├── alembic.ini           # Конфигурация Alembic
├── .env.example          # Пример переменных окружения
└── README.md             # Документация
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | Строка подключения к PostgreSQL | `postgresql+asyncpg://...` |
| `SECRET_KEY` | Секретный ключ для JWT | `your-super-secret-key...` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access токена | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh токена | `7` |
| `ALGORITHM` | Алгоритм подписи JWT | `HS256` |
| `CORS_ORIGINS` | Разрешенные CORS origins | `["http://localhost:3000"]` |
| `DEBUG` | Режим отладки | `false` |

## База данных

### Миграции

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "Add users table"

# Применить миграции
alembic upgrade head

# Откатить на одну миграцию назад
alembic downgrade -1
```

### Модель User

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для производительности
CREATE INDEX idx_user_email_active ON users(email, is_active);
CREATE INDEX idx_user_username_active ON users(username, is_active);
```

## Безопасность

- ✅ Bcrypt для хеширования паролей
- ✅ JWT токены с коротким временем жизни
- ✅ Refresh токены для обновления
- ✅ Валидация email и пароля
- ✅ Non-root user в Docker контейнере
- ✅ Обработка исключений без утечки информации
- ✅ CORS настройки
- ✅ SQL injection защита (SQLAlchemy ORM)

## Разработка

### Тестирование

```bash
# Установить dev зависимости
pip install pytest pytest-asyncio httpx

# Запустить тесты
pytest
```

### Линтинг и форматирование

```bash
# Black форматирование
black app/

# Ruff линтинг
ruff check app/

# Type checking
mypy app/
```

## Production готовность

- ✅ Multi-stage Docker build
- ✅ Health checks
- ✅ Graceful shutdown
- ✅ Connection pooling
- ✅ Structured logging
- ✅ Request ID tracing
- ✅ Error handling
- ✅ Configuration management
- ✅ Database migrations

## API Документация

После запуска сервиса документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc