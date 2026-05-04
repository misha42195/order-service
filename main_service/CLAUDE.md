# CLAUDE.md

Этот файл содержит рекомендации для Claude Code (claude.ai/code) при работе с кодом в этом репозитории.

## Описание проекта

SFMShop — интернет-магазин на FastAPI с PostgreSQL, Redis и MongoDB. Архитектура готова к микросервисам.

## Запуск приложения

```bash
# Разработка с авто-перезагрузкой
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# С помощью Docker Compose
docker-compose up --build

# Запуск тестов
pytest testing/

# Тесты с покрытием
pytest testing/ --cov
```

## Архитектура

```
api/main.py          # Точка входа FastAPI, агрегация роутеров
api/routs/           # Обработчики маршрутов (products, orders, users, login)
core/config.py       # Настройки через pydantic-settings
database/models.py   # SQLAlchemy async модели (User, Product, Order, OrderItem)
services/            # Бизнес-логика
repositories/        # Уровень доступа к данным
models/              # Pydantic модели и исключения
```

## Ключевые технологии

- **Фреймворк**: FastAPI + Uvicorn
- **База данных**: PostgreSQL с SQLAlchemy 2.0 (async) и asyncpg
- **Кэш**: Redis
- **Логирование**: MongoDB (база sfmshop_logs)
- **Авторизация**: JWT через python-jose, пароли через bcrypt

## Настройки

Настройки хранятся в `.env` файле и `core/config.py`. Переменные окружения используют двойное подчёркивание для вложенных групп (например, `DATABASE__DB_HOST`). Приложение работает на порту 8000.

## Структура API

Все маршруты имеют префикс `/api/v1`:
- `GET /api/v1/products` — список товаров
- `POST /api/v1/orders` — создание заказа
- `GET /api/v1/users` — список пользователей

## Модели базы данных

SQLAlchemy async модели в `database/models.py`: User, Product, Order, OrderItem. Операции выполняются асинхронно через `database/connection.py`.

## Внешние сервисы

Взаимодействие с внешними API идёт через `services/external_api_service.py`. API-ключ Anthropic настраивается через переменную окружения `ANTHROPIC_API_KEY`.