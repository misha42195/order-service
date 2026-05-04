# Docker для начинающих

## Основные понятия

### Образ (Image) vs Контейнер (Container)

| Термин | Аналогия |
|--------|----------|
| **Образ** | Рецепт торта на бумаге |
| **Контейнер** | Готовый торт в коробке |

```bash
docker pull postgres:17    # Скачать "рецепт" (образ) из интернета
docker run --name my-db   # Создать и запустить "блюдо" (контейнер)
```

Из одного образа можно создать много контейнеров.

---

## Dockerfile — инструкция по сборке

### Структура Dockerfile

```dockerfile
FROM python:3.12-slim          # 1. Базовый образ (какая коробка с Python)
WORKDIR /app                    # 2. Рабочая папка (поставь на стол)
COPY requirements.txt .         # 3. Скопируй список ингредиентов
RUN pip install --no-cache-dir -r requirements.txt  # 4. Установи всё из списка
COPY . .                        # 5. Скопируй весь код на стол
EXPOSE 8000                     # 6. Открой порт 8000 (сделай дверь)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]  # 7. Запусти
```

### Аналогия с тортом

| Строка Dockerfile | Аналогия |
|------------------|----------|
| `FROM` | "Возьми готовую основу для торта" |
| `WORKDIR` | "Расчисть стол под работу" |
| `COPY` | "Положи ингредиенты на стол" |
| `RUN` | "Смешай, испеки" |
| `EXPOSE` | "Сделай дырку для выхода пара" |
| `CMD` | "Теперь можно есть!" |

### Что происходит при `docker build` и `docker run`

```bash
docker build -t myapp .           # Собираем образ из Dockerfile
docker run -d --name myapp myapp  # Запускаем контейнер из образа
```

**Этапы сборки:**
1. Docker читает Dockerfile
2. Скачивает базовый образ (если нет)
3. Создаёт промежуточные слои (каждый RUN = новый слой)
4. Копирует файлы приложения
5. Сохраняет результат как образ

---

## Multi-stage Build — оптимизация размера образа

### Зачем это нужно?

| Без multi-stage | С multi-stage |
|-----------------|---------------|
| Образ: ~1.2 GB | Образ: ~150 MB |
| Включает компилятор, dev-библиотеки | Только код и runtime |

### Как это работает

```
Этап 1 (повар):    Приготовил блюдо, почистил овощи, нарезал мясо
Этап 2 (официант): Взял только готовое блюдо и подал на стол
                   (мусор, очистки, посуда — остались на кухне)
```

### Пример multi-stage для Python

```dockerfile
# Этап 1: Сборка (тяжёлый образ с компилятором)
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt   # Устанавливаем с зависимостями
COPY . .

# Этап 2: Финальный образ (лёгкий, только код)
FROM python:3.12-slim

WORKDIR /app

# Копируем ТОЛЬКО установленные пакеты из этапа 1
COPY --from=builder /root/.local /root/.local

# Копируем только нужные папки с кодом
COPY --from=builder /app/api ./api
COPY --from=builder /app/core ./core
COPY --from=builder /app/database ./database
COPY --from=builder /app/services ./services

# PATH для пользовательских пакетов
ENV PATH=/root/.local:$PATH

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Ключевые команды multi-stage

```dockerfile
FROM image AS builder              # Дать имя этапу (AS builder)
COPY --from=builder /src /dest    # Скопировать из конкретного этапа
```

### Пример для Go (крайний случай)

```dockerfile
# Этап 1: Компиляция
FROM golang:1.22 AS builder
WORKDIR /app
RUN go build -o myapp main.go

# Этап 2: Минимальный образ
FROM scratch                        # Пустой образ, только бинарник
COPY --from=builder /app/myapp /myapp
CMD ["/myapp"]
# Итог: 10 MB вместо 800 MB
```

---

## .dockerignore — что НЕ копировать в образ

### Зачем?

Без `.dockerignore` в образ попадает всё: `.git`, `__pycache__`, логи, тесты, docs. Это увеличивает размер и засоряет образ.

### Пример .dockerignore

```bash
# Python
__pycache__
*.pyc
*.pyo
*.pyd
*.egg-info
dist
build

# Git
.git
.gitignore

# IDE
.idea
.vscode

# Logs
*.log
logs

# Tests
*.test.py
testing
tests_test

# Docs
docs
*.md

# Docker
docker-compose.yaml
Dockerfile
.dockerignore

# Environments
.env
.env.*
```

---

## Команды Docker

### Работа с образами

```bash
docker images                          # Показать все скачанные образы на компьютере
docker pull ubuntu:latest              # Скачать образ ubuntu из интернета
docker rmi ubuntu:latest               # Удалить скачанный образ
docker build -t myapp .                # Собрать образ из Dockerfile (в текущей папке)
docker build -t myapp -f docker/Dockerfile .  # Собрать из конкретного пути
```

### Работа с контейнерами

```bash
docker ps                              # Показать только работающие контейнеры
docker ps -a                           # Показать ВСЕ контейнеры (включая остановленные)
docker run -d --name my-app ubuntu     # Создать и запустить НОВЫЙ контейнер (в фоне)
docker run -it ubuntu bash             # Запустить и сразу войти внутрь (интерактивно)
docker stop my-app                     # ОСТАНОВИТЬ работающий контейнер
docker start my-app                    # ЗАПУСТИТЬ остановленный контейнер заново
docker restart my-app                  # Перезапустить контейнер
docker rm my-app                       # УДАЛИТЬ остановленный контейнер
docker rm -f my-app                    # УДАЛИТЬ работающий контейнер (force)
```

### Логи и отладка

```bash
docker logs my-app                     # Посмотреть логи контейнера (вывод программы)
docker logs -f my-app                   # Следить за логами в реальном времени (follow)
docker exec -it my-app bash            # Зайти ВНУТРЬ работающего контейнера
docker exec my-app ps aux              # Выполнить команду внутри контейнера (без входа)
docker inspect my-app                  # Посмотреть всю информацию о контейнере
docker stats                           # Посмотреть нагрузку (CPU, RAM) всех контейнеров
```

### Работа с сетями

```bash
docker network connect bridge my-container   # Подключить контейнер к сети bridge
docker network disconnect bridge my-container  # Отключить контейнер от сети
docker network inspect bridge                # Посмотреть кто в сети bridge
```

---

## Сети Docker

### Проблема: контейнеры не видят друг друга

Контейнеры запущенные отдельно (не через docker-compose) могут оказаться в разных сетях и не видеть друг друга.

```
postgres (в одной сети)  ←→  sfmshop app (в другой сети) = ОШИБКА Connection Refused
```

### Решение: подключить к одной сети

```bash
docker network connect bridge sfmshop
```

### Как работают имена контейнеров

В docker-compose контейнеры обращаются друг к другу по **имени сервиса**:
```yaml
services:
  app:
    # Здесь app обращается к базе по имени "db"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/sfmshop
  db:
    image: postgres:17
```

`db` — это имя сервиса, оно же становится DNS-именем внутри сети.

---

## Docker Compose — запуск нескольких контейнеров

### Зачем нужен Docker Compose?

Вручную запускать много контейнеров сложно:
```bash
# Это муторно:
docker run -d --name db postgres:17
docker network connect bridge db
docker run -d --name redis redis:7-alpine
docker network connect bridge redis
docker run -d --name app --network bridge myapp
# ...и так для каждого
```

Docker Compose делает это одной командой: `docker compose up`

### Структура docker-compose.yaml

```yaml
services:                              # Секция контейнеров
  app:                                 # Сервис 1: приложение
    build:
      context: ..
      dockerfile: docker/Dockerfile   # Путь к Dockerfile
    networks:
      - app_network                   # Подключение к сети
    ports:
      - "8000:8000"                   # Проброс портов: хост:контейнер
    environment:                      # Переменные окружения
      - DB_USER=user
      - DB_PASSWORD=password
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379
    depends_on:                        # Запустить ПОСЛЕ этих сервисов
      - db
      - redis
    healthcheck:                      # Проверка здоровья контейнера
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:                                  # Сервис 2: база данных
    networks:
      - app_network
    image: postgres:17
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=sfmshop
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d sfmshop"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:                               # Сервис 3: кэш
    networks:
      - app_network
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:                               # Именованные тома для данных
  postgres_data:                       # Данные postgres сохранятся после перезапуска

networks:                              # Кастомные сети
  app_network:
    driver: bridge
```

### Команды Docker Compose

```bash
docker compose up              # Запустить все сервисы (из docker-compose.yaml)
docker compose up -d           # Запустить в фоне (detached)
docker compose up --build     # Пересобрать образы и запустить
docker compose down           # Остановить и удалить все контейнеры
docker compose down -v        # Остановить и УДАЛИТЬ тома (данные тоже удалятся!)
docker compose ps             # Показать статус всех сервисов
docker compose logs app       # Посмотреть логи конкретного сервиса
docker compose logs -f app   # Следить за логами app в реальном времени
docker compose exec app bash  # Зайти внутрь контейнера app
docker compose exec db psql -U user -d sfmshop  # Подключиться к postgres
docker compose restart app   # Перезапустить только app
docker compose top            # Показать процессы внутри контейнеров
```

### build и context — важно!

```yaml
# Правильно: указываем context и dockerfile
app:
  build:
    context: ..
    dockerfile: docker/Dockerfile

# Правильно: просто build использует Dockerfile в той же папке
app:
  build: .
```

---

## Healthcheck — проверка здоровья

### Что это?

Healthcheck позволяет Docker понять, что контейнер готов принимать соединения (а не просто запущен).

### Примеры healthcheck

```yaml
# Для веб-приложения (curl)
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3

# Для PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U user -d sfmshop"]
  interval: 10s
  timeout: 5s
  retries: 5

# Для Redis
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Зачем нужен?

- Контейнер "healthy" только когда healthcheck проходит
- `depends_on` с healthcheck ждёт готовности, не просто запуска
- Можно увидеть статус в `docker compose ps`

---

## Частые проблемы и решения

### Порт уже занят

```
Error: ports are not available: exposing port TCP 6379 -> bind: address already in use
```

**Решение 1:** Остановить процесс на хосте
```bash
sudo systemctl stop redis   # для Linux
```

**Решение 2:** Изменить порт в docker-compose.yaml
```yaml
ports:
  - "6380:6379"    # Теперь redis на хосте доступен по 6380
```

### Контейнеры не видят друг друга

```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Причина:** Контейнеры в разных сетях.

**Решение:** Использовать docker-compose (все сервисы в одной сети) или:
```bash
docker network connect bridge ИМЯ_КОНТЕЙНЕРА
```

### База данных не найдена

```
relation "orders" does not exist
```

**Причина:** Таблицы не созданы. Миграции не запущены.

**Решение:**
```bash
docker compose exec app alembic upgrade head
```

### Foreign Key ошибка

```
ForeignKeyViolationError: Key (user_id)=(0) is not present in table "users"
```

**Причина:** Код пытается создать запись с несуществующим foreign key.

**Это уже ошибка в логике приложения, не Docker.**

### Проблема с переменными окружения

Код читает `DB_USER`, но в docker-compose установлена только `DATABASE_URL`.

**Решение:** Убедись что все переменные установлены:
```yaml
environment:
  - DATABASE_URL=postgresql://user:password@db:5432/sfmshop
  - DB_USER=user
  - DB_PASSWORD=password
  - DB_HOST=db
  - DB_PORT=5432
  - DB_NAME=sfmshop
```

---

## Volumes — сохранение данных

### Зачем нужны volumes?

По умолчанию данные контейнера живут только пока контейнер живёт. Остановил → удалил → данные потеряны.

Volumes позволяют сохранить данные.

### Пример с postgres

```yaml
services:
  db:
    image: postgres:17
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Сохраняем папку с данными

volumes:
  postgres_data:    # Docker создаст том и будет хранить данные на хосте
```

### Команды для работы с volumes

```bash
docker compose down          # Контейнеры остановлены, данные сохранены
docker compose up -d         # Данные на месте
docker compose down -v       # Удалить ВСЁ включая volumes
docker volume ls             # Список всех томов
docker volume inspect volume_name  # Информация о томе
```

---

## Переменные окружения в Docker

### В docker-compose

```yaml
environment:
  - DB_USER=user               # Строковые значения
  - DB_PORT=5432               # Можно без кавычек
  - DEBUG=true                 # Boolean как строку
```

### В Dockerfile

```dockerfile
ENV DEBUG=false              # Установить переменную при сборке образа
```

### Чтение в Python приложении

```python
# Из переменных окружения напрямую
import os
db_user = os.getenv("DB_USER", "default_user")

# Из pydantic_settings (как в проекте SFMShop)
from pydantic_settings import BaseSettings
class DatabaseSettings(BaseSettings):
    DB_USER: str = ""         # Читает из переменной DB_USER
    DB_HOST: str = ""         # Читает из переменной DB_HOST

# Или из REDIS_URL (для Redis)
import os
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
```

### Проверить переменные в контейнере

```bash
docker compose exec app env | grep DB_   # Показать только DB_ переменные
docker compose exec app env              # Показать все переменные
```

---

## Полезные советы

### Очистка

```bash
docker system prune              # Удалить неиспользуемые образы, контейнеры, сети
docker system prune -a           # Удалить ВСЕ неиспользуемые образы
docker container prune           # Удалить остановленные контейнеры
docker image prune               # Удалить неиспользуемые образы
docker volume prune              # Удалить неиспользуемые тома
```

### Проверка

```bash
docker ps                       # Работающие контейнеры
docker ps -a                    # Все контейнеры
docker images                   # Все образы
docker volume ls                # Все тома
docker network ls               # Все сети
```

### Скопировать файл из контейнера / в контейнер

```bash
docker cp my-container:/app/logs/error.log ./error.log    # Из контейнера на хост
docker cp ./config.txt my-container:/app/config.txt      # С хоста в контейнер
```

---

## Проект SFMShop — структура Docker

```
SFMShop/
└── main-service/
    ├── docker/
    │   └── Dockerfile          # Multi-stage build (оптимизированный)
    ├── docker-compose.yaml      # app + db + redis
    ├── .dockerignore            # Исключения для сборки
    ├── api/                     # FastAPI эндпоинты
    ├── core/config.py           # Настройки из env переменных
    ├── database/connection.py   # Подключение к PostgreSQL
    ├── services/cache_service.py # Redis кэш (читает REDIS_URL)
    └── migration/               # Alembic миграции
```

### Как запустить проект

```bash
cd main-service_clode
docker compose up --build       # Собрать и запустить всё
docker compose exec app alembic upgrade head  # Применить миграции
```

### Переменные окружения в проекте

| Переменная | Описание | Где используется |
|------------|----------|------------------|
| `DB_USER` | Пользователь PostgreSQL | database/connection.py |
| `DB_PASSWORD` | Пароль PostgreSQL | database/connection.py |
| `DB_HOST` | Хост PostgreSQL | database/connection.py |
| `DB_PORT` | Порт PostgreSQL | database/connection.py |
| `DB_NAME` | Имя базы данных | database/connection.py |
| `REDIS_URL` | URL Redis | services/cache_service.py |

---

## Краткая шпаргалка

```bash
# Сборка и запуск
docker build -t myapp .                           # Собрать образ
docker run -d --name myapp myapp                   # Запустить контейнер
docker compose up --build                          # Собрать и запустить все сервисы
docker compose up -d                               # Запустить в фоне

# Управление
docker stop myapp                                  # Остановить
docker start myapp                                 # Запустить
docker rm myapp                                    # Удалить

# Логи и отладка
docker logs myapp                                  # Посмотреть логи
docker logs -f myapp                               # Следить за логами
docker exec -it myapp bash                         # Зайти внутрь

# Docker Compose
docker compose ps                                  # Статус сервисов
docker compose logs app                            # Логи app
docker compose exec app bash                       # Зайти в app
docker compose exec db psql -U user -d sfmshop     # Подключиться к postgres
docker compose down                                # Остановить всё
docker compose down -v                             # Остановить всё и удалить тома

# Миграции базы данных
docker compose exec app alembic current            # Проверить миграцию
docker compose exec app alembic upgrade head        # Применить миграции
docker compose exec app alembic downgrade -1        # Откатить миграцию
```

---

## Команды, которые мы учили

| Команда | Что делает |
|---------|------------|
| `docker pull` | Скачать образ |
| `docker run` | Создать и запустить контейнер |
| `docker build` | Собрать образ из Dockerfile |
| `docker build -f docker/Dockerfile` | Собрать из конкретного Dockerfile |
| `docker compose up` | Запустить всё по docker-compose.yaml |
| `docker compose up --build` | Пересобрать и запустить |
| `docker compose exec` | Выполнить команду внутри сервиса |
| `docker network connect` | Подключить контейнер к сети |
| `docker volume ls` | Показать все тома |
| `docker logs -f` | Следить за логами в реальном времени |
