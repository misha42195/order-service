

# Использовать официальный образ Python
FROM python:3.12-slim

# Установить рабочую директорию
WORKDIR /app

# Копировать requirements.txt
COPY requirements.txt .

# Установить зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копировать код приложения
COPY . .

# Открыть порт
EXPOSE 8000

# Запустить приложение
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
