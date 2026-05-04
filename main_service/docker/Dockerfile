# Этап 1: Сборка (builder)
FROM python:3.12-slim AS builder

WORKDIR /app

# Копируем только requirements и устанавливаем зависимости
COPY requirements.txt .

# Устанавливаем зависимости в пользовательскую папку
RUN pip install --user -r requirements.txt

# Копируем весь код
COPY . .

# Этап 2: Финальный образ
FROM python:3.12-slim

WORKDIR /app

# Копируем установленные зависимости из этапа 1
COPY --from=builder /root/.local /root/.local

# Копируем только код приложения (без лишних файлов)
COPY --from=builder /app/api ./api
COPY --from=builder /app/core ./core
COPY --from=builder /app/database ./database
COPY --from=builder /app/models ./models
COPY --from=builder /app/repositories ./repositories
COPY --from=builder /app/services ./services
COPY --from=builder /app/rest ./rest
COPY --from=builder /app/schemas ./schemas
COPY --from=builder /app/utils ./utils
COPY --from=builder /app/dependencies.py ./dependencies.py
COPY --from=builder /app/middleware.py ./middleware.py
COPY --from=builder /app/alembic.ini ./alembic.ini
COPY --from=builder /app/migration ./migration

# Устанавливаем переменную PATH для пользовательских пакетов
ENV PATH=/root/.local:$PATH

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]