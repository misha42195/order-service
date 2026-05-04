Настройка виртуального окружения для проекта SFMShop
##1. ШАГ

### Создание виртуального окружения

```shell
cd SFMShpo # переход в директорию проекта
```

### Создать виртуальное окружения

```shell
python -m venv venv # создание виртуального окружения с названием venv
```

## ШАГ.2

### Активация виртуального окружения

```shell
source venv/bin/activate # Linux/MacOS
venv\Scripts\activate
```

## Шаг.3

### Установка зависимостей проекта.
```shell
pip install fastapi[standart]

# или установка зависимостей из requirements.txt
pip install -r requirements.txt
```

## Шаг.4
### Обновление requirements.txt
```shell
# сохранение зависимостей
pip freeze > requirements.txt
```

## Шаг.5
### Проверка окружения
```shell
pip list
python --version
```
