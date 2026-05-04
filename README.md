# SFMShop

Интернет-магазин для продажи товаров. Проект для изучения Python на практике.

## Быстрый старт

### 1. Настройка виртуального окружения

```bash
cd SFMShop
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate   # Windows
pip install -r main-service/requirements.txt
```

### 2. Переменные окружения

Настройте подключение к БД в `main-service/.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=password
MONGO_URL=mongodb://localhost:27017/
```

### 3. Запуск сервисов

**RabbitMQ:**
```bash
cd main-service
docker compose up -d
```
- UI: http://localhost:15672 (guest/guest)
- AMQP: localhost:5672

**PostgreSQL** — локально или через Docker.

### 4. Запуск приложения

```bash
cd main-service
uvicorn main:app --reload
```
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 5. Проверка окружения

```bash
pip list
python --version
```

## Структура проекта

```
SFMShop/
├── main-service/       # FastAPI сервис
│   ├── api/            # Роуты
│   ├── core/           # Конфигурация
│   ├── models/         # Модели данных
│   ├── repositories/   # Работа с БД
│   ├── services/       # Бизнес-логика
│   ├── docs/           # Документация
│   └── docker-compose.yaml
├── migrations/         # Миграции Alembic
└── test.http           # Коллекция HTTP-запросов
```

## Сервисы

| Сервис      | Порт      | Описание                   |
|-------------|-----------|----------------------------|
| FastAPI     | 8000      | Основной API               |
| Swagger UI  | 8000/docs | Интерактивная документация |
| RabbitMQ    | 5672      | Message broker             |
| RabbitMQ UI | 15672     | Управление очередями       |
| PostgreSQL  | 5432      | Реляционная БД             |
| MongoDB     | 27017     | NoSQL БД                   |

## Команды

```bash
# Обновление зависимостей
pip freeze > main-service/requirements.txt

# Миграции БД
alembic upgrade head

# Запуск тестов
pytest
```
