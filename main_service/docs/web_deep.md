from typing import Annotatedfrom starlette.requests import Requestfrom src.database.models import Orderfrom src.database.connection import SessionLocalfrom src.database.connection import SessionLocal

1.

Процесс загрузки веб-страницы (10 баллов)

Объясни все этапы загрузки веб-страницы:
DNS-запрос, TCP-подключение, HTTP-запрос,
обработка на сервере, HTTP-ответ, рендеринг.
Как можно оптимизировать каждый этап?

```text
Этапы загрузки веб-страницы.
1) Запрос к DNS-серверу для получения IP-адреса по доменному 
имени. Если уже обращались к DNS то получим IP из кеша
(Проблема несохранениея IP в кеш DNS, выбираем хороший DNS-сервер) 
2) TCP-подключение протокол для передачу данных между клиентом
и сервером. Это установка соединения с сервером для отправки запроса. 
3) После установки соединения отправляем HTTP-запрос c определенным методом.
Указывается путь для представледния и заголовок с метададнными.(
Использовение кеширования что бы минимзировать кол-во запросов) 
4) Сервер получаем запрос, находит нужное представление для указанного маршрута.
(Проблемы: при каждом запросе ходим в БД нужно кеширование Redis,
Получение слишком больших данных, нужная пагинация и кеш на стороне клиента
Нептимизированная база в котором нет интексов в базе для получения часто запрашиваемых данных
Шардирование и репликация для чтения отдельная база, для обновления создания удаления другая
При обработке на стороен сервера реализован неоптимальный алгоритм, оптимизация кода,
Использование асинхронных методов обработки запроса)
5) После обработки отправляет HTTP-ответ с кодом статуса, 
контентом, и заголовками(). 
6) Клиент получаем ответ и рендерит страницу. Строит DOM, подгружает CSS и JS.
```

2.

```python
# Создание FastAPI endpoint с валидацией (15 баллов)
# 
# Создать FastAPI endpoint для создания товара с валидацией через Pydantic. Endpoint должен принимать данные товара (name, price, stock), валидировать их и возвращать созданный товар.
# 
# Pydantic модель для валидации
# FastAPI endpoint с POST методом
# Валидацию полей (name не пустое, price > 0, stock >= 0)
# Правильный HTTP-статус (201 Created)


# from fastapi import FastAPI, Depends, HTTPException
# from pydantic import BaseModel, Field, NonNegativeInt, field_validator
# from sqlalchemy.orm import Session
# from starlette import status
# from typing import Annotated
# 
# from annotated_types import (
#     MaxLen,
#     MinLen,
#     Gt,
# )
# 
# from src.database.connection import get_db
# from src.database.models import Product
# 
# app = FastAPI()
# 
# 
# # Схема для создания товара с валидацией
# class ProductCreate(BaseModel):
#     # валидация длины названия товара от 3 до 30 символов
#     name: Annotated[
#         str,
#         MinLen(3),
#         MaxLen(30),
#     ]
# 
#     # цена товара больше чем 0 руб
#     price: Annotated[
#         float,
#         Gt(0),
#     ]
#     stock: NonNegativeInt  # количество неотрицательное
# 
#     @field_validator("name")
#     def check_name(v: str) -> str:
#         # Проверяем, что после удаления пробелов строка не пуста
#         if not v.strip():
#             raise ValueError("Имя не может быть пустым")
#         return v.strip()
# 
# 
# @app.post(
#     "/products",
#     status_code=status.HTTP_201_CREATED,
# )
# def create_product(
#         product_in: ProductCreate,
#         db: Session = Depends(get_db),
# ):
#     try:
#         product_in_db = db.query(Product).where(Product.name == product_in.name).first()
#         if product_in_db:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail=f"Продукт с именем {product_in.name} уже существует",
#             )
#         new_product = Product(
#             **product_in.model_dump(),
#         )
#         db.add(new_product)
#         db.commit()
#         db.refresh(new_product)
#         return new_product
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Ошибка сохранения данных в базу {e}",
#         )
```

3

```python
# Middleware для логирования (15 баллов)
# 
# Создать middleware для логирования всех запросов в FastAPI. Middleware должен логировать метод, путь, время выполнения и статус ответа.
# 
# Middleware с использованием @app.middleware("http")
# Логирование метода и пути запроса
# Измерение времени выполнения
# Логирование статуса ответа
# Добавление заголовка с временем выполнения

# import logging
# 
# # Конфигурация
# LOG_LEVEL = logging.INFO
# DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# LOG_FORMAT = (
#     "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
# )
# 
# # Настройка
# logging.basicConfig(
#     level=LOG_LEVEL,
#     format=LOG_FORMAT,
#     datefmt=DATE_FORMAT,
# )
# 
# # Создаем экземпляр логгера
# logger = logging.getLogger(__name__)
# 
# app = FastAPI()
# 
# 
# @app.middleware("http")
# async def logging_of_all_requests(
#         request: Request,
#         call_next,
# ):
#     # до запроса
#     start_time = time.time()
#     method = request.method  # получение медода запроса
#     path = request.url.path  # получение пути запроса
#     response = await call_next(request)
#     status_code = response.staus_code
#     # после обработки запроса
#     process_time = time.time() - start_time
#     logger.info(
#         f"Method: {method}, Path: {path}",
#         f"Status: {status_code}, Time: {process_time}",
#     )
#     response.headers["Process-Time"] = process_time
#     return response
```


4 
# HTTP-методы и статусы (10 баллов)

#   

# Объясни разницу между HTTP-методами

# GET, POST, PUT, PATCH, DELETE.

# Когда использовать каждый метод?

# Какие HTTP-статусы использовать для каждого метода?

GET
Когда использовать:
Для получения данных без изменения сервера (например, получение списка продуктов).
не меняет состояние на сервере (одинаковый запрос всегда возвращает одинаковый результат).
Пример:

200 OK: Запрос успешно обработан и возвращены данные.
404 Not Found: Ресурс не найден.
500 Internal Server Error: Внутренняя ошибка сервера.

POST
Когда использовать:
Для создания новых объектов на сервере.
Отправки данных, которые могут изменить состояние сервера (например, отправка формы).
статусы длля POST:
201 Created: Объект создан успешно.
400 Bad Request: Запрос некорректен (например, неверные данные).
403 Forbidden: Доступ запрещен.
500 Internal Server Error: Внутренняя ошибка сервера.

PUT
Когда использовать:
Для обновления существующих объектов на сервере.
Полностью заменяет существующий объект новым полями.
статусы для PUT:
200 OK: Ресурс успешно обновлен.
404 Not Found: Ресурс не найден.
400 Bad Request: Запрос некорректен (например, неверные данные).
403 Forbidden: Доступ запрещен.
500 Internal Server Error: Внутренняя ошибка сервера.

PATCH
Когда использовать:
Для частичного обновления существующих объектов на сервере.
Применяется когда нужно изменить только некоторые поля объекта.
статусы для PATCH:
200 OK: Объект успешно обновлен.
404 Not Found: объект не найден.
400 Bad Request: Запрос некорректен (например, неверные данные).
403 Forbidden: Доступ запрещен.
500 Internal Server Error: Внутренняя ошибка сервера.

DELETE
Когда использовать:
Для удаления существующих ресурсов с сервера.
Пример:
204 No Content: Объект успешно удален.
404 Not Found: Объект не найден.
403 Forbidden: Доступ запрещен.
500 Internal Server Error: Внутренняя ошибка сервера.

Чтение данных (например, получить список продуктов).
Без изменений на сервере.
POST:

Создание нового ресурса (например, добавить новый продукт).
Изменения на сервере.
PUT:

Полное обновление существующего ресурса.
Полная замена данных на сервере.
PATCH:

Частичное обновление существующего ресурса.
Изменение только определенных полей.
DELETE:

Удаление существующего ресурса.
----------------------------------------------
5 5.
Dependency Injection для БД (15 баллов)

Создать зависимость для подключения к БД через Dependency Injection. Использовать Depends для передачи подключения к БД в endpoints.

Функцию-зависимость для БД
Использование yield для закрытия подключения
Использование Depends в endpoint
Правильное управление подключением

```python
# from dotenv import load_dotenv
# from fastapi import FastAPI, Depends
# from sqlalchemy import URL, create_engine
# from sqlalchemy.orm import sessionmaker, Session
# 
# from src.database.connection import env_path
# from src.database.models import Product
# 
# app = FastAPI()
# load_dotenv(dotenv_path=env_path)
# 
# DB_URL = URL.create(
#     drivername="postgresql",
#     username=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),  # Пароль из .env
#     host=os.getenv("DB_HOST"),
#     port=int(os.getenv("DB_PORT")),
#     database=os.getenv("DB_NAME"),
# )
# engine = create_engine(DB_URL)
# SessionLocal = sessionmaker(bind=engine)
# 
# 
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
# 
# 
# @app.get("/products")
# def get_products(db: Session = Depends):
#     producs = db.query(Product).all()
#     return {"products": producs}
```
6.
REST API принципы (10 баллов)

Объясни принципы REST API. 
Как правильно проектировать RESTful endpoints? 
Приведи примеры правильной и неправильной 
структуры endpoints.

Rest API - это архитектурный стиль проектирования веб приложения
для которого характерны следующие приныпы 

1 -￼Ресурсы￼￼ - все данные представлены как ресурсы (то есть данные которые 
мы запрашиваем от сервера например продукты, пользователи, заказы) В
url-маршруте мы указываем существительное во множественном числе например /products или /products/{id}
2 HTTP-методы￼￼ - используем  HTTP-методы (для получения GET,для создания ресурса POST,длля полного обновления
PUT, PATCH для частичного обновеления,  DELETE для удалендия ресурса) 
3 Статус коды в ответах от сервера - используются стандартные HTTP-статусы
4 Без состояния￼- каждый запрос независим и содержит всю необходимую информацию, 
# ----------------------------------------------------------
Работа с внешним API (15 баллов)

Создать клиент для работы с внешним API курсов валют. Реализовать получение курса валют с обработкой ошибок и retry-логикой.

Класс для работы с внешним API
Обработку ошибок (Timeout, ConnectionError)
Retry-логику с экспоненциальной задержкой
Возврат результата или None при ошибке
```python
# import requests
# from requests import Timeout, RequestException
# 
# 
# class Exchange:
#     def __init__(
#         self,
#         url: str = "https://v6.exchangerate-api.com/v6/d523029a0a73b04cb4e3d6fe/latest/",
#     ):
#         self.url = url
#         self.max_retry = 3
#         self.timeout = 5
# 
#     def get_exchange_rate(
#         self,
#         base_currency: str,
#         target_currency: str,
#     ):
#         for attempt in range(self.max_retry):
#             try:
#                 response = requests.get(
#                     f"{self.url}/{base_currency}",
#                     timeout=self.timeout,
#                 )
#                 if response.status_code == 200:  # Проверка успешности запроса
#                     data = response.json()
# 
#                     if target_currency in data.get("conversion_rates", {}):
#                         return data["conversion_rates"][target_currency]
#                     else:
#                         print(f"Валюта {target_currency}  не найдена")
#             except (
#                 Timeout,
#                 ConnectionError,
#             ) as e:  # обработка ошибок Timeout, ConnectionError
#                 self.handle_network_error(e, attempt)
# 
#             except RequestException as e:
#                 raise e
#         return None
# 
#     def handle_network_error(self, error, attempt):
#         """Метод для обработки Timeout и ConnectionError"""
#         delay = 2**attempt
#         if attempt < self.max_retry - 1:
#             print(f"{error}, повтор через {delay}")
#             time.sleep(delay)
#         else:
#             print("Превышено время ожидания после всех попыток")
# 
#     def convert_price(
#         self,
#         price: float,
#         from_currency: str,
#         to_currency: str,
#     ) -> [float]:
#         """Конвертировать цену из одной валюты в другую"""
#         if from_currency == to_currency:
#             return price
#         rate = self.get_exchange_rate(
#             from_currency,
#             to_currency,
#         )
#         if rate is None:
#             return None
#         return price * rate
# 
# 
# if __name__ == "__main__":
#     client = Exchange()
#     converted_price = client.convert_price(
#         1000,
#         "USD",
#         "THB",
#     )
#     if converted_price:
#         print(f"1000 USD = {converted_price}")
#     else:
#         print("Не удалось получить курс валют")

```
Объясни, что такое Dependency Injection в FastAPI. 
Как использовать Depends для передачи зависимостей? 
Приведи пример использования для БД и аутентификации.
Dependency Injection - или внедрение зависимостей - это 
функция которая принимает вызываемый объект(callable объект) 
вызывает его, получает результать на месте вызова и значение уже 
присваивается параметру внутри функции представления

примеры для базы данных и аутентификации

```python
# from fastapi import (
#     FastAPI,
#     Depends,
#     HTTPException,
#     status,
# )
# from typing import Annotated
# from fastapi.security import (
#     HTTPBearer,
#     HTTPAuthorizationCredentials,
# )
# from jose import jwt, JWTError
# from src.database.connection import SessionLocal
# from sqlalchemy.orm import Session
# 
# SECRET_KEY = "your-secret-key"
# ALGORITHM = "HS256"
# 
# 
# app = FastAPI()
# security = HTTPBearer()
# 
# 
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
# 
# 
# def verify_token(token: str):
#     """Проверить JWT токен и вернуть id пользователя"""
#     try:
#         payload = jwt.decode(
#             token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM],
#         )
#         return payload.get("id")
#     except JWTError:
#         return None
# 
# 
# static_api_token = HTTPBearer(
#     scheme_name="Static API-token",
#     description="Для входа введите токен",
#     auto_error=False,  # запрос без токена -> ошибка
# )
# 
# 
# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials | None = Depends(static_api_token),
# ):
#     if credentials is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Нужно авторизоваться",
#         )
# 
#     user_data = verify_token(credentials.credentials)
#     if not user_data:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Невалидный токен",
#         )
#     return user_data
# 
# 
# @app.get("/orders")
# def get_user(
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     orders = db.query(Order).filter(Order.user_id == user_id).all()
#     return {"orders": orders}

```
9.
Проектирование REST API (15 баллов)

Спроектировать структуру REST API для работы с товарами. 
Описать все endpoints с указанием HTTP-методов, 
путей и статусов.

GET products/ - получение списка продуктов 200 OK при успехе, 404 NOT Found если продукты не найдены 
GET products/{product_id} - получение продукта по product_id 200 OK при успехе, 404 если продукт по id не найден
POST products/ - создание продукта 201 Created 
PUT products/{product_id} - полное обновление продукта 200 OK
PATCH products/{product_id} - частичное обновление продукта 200 OK
DELETE products/{product_id} - удаление продукта по id 204 NO Content
# ---------------------------------------------------------

10.
Middleware в FastAPI (10 баллов)

Объясни, что такое middleware в FastAPI. 
Как создать middleware для логирования запросов? 
Приведи пример middleware с измерением времени выполнения.

Middleware - это функция-промежуточный слой, 
который выполняется до того как запрос уйдет 
на серавер и до того как клиент получит ответ от сервера
Можем реализовать логирование, измерение времени, можем 
добавлять дополнительную инфу в заголовки.

```python
# import time
# from fastapi import FastAPI, Request
# from datetime import datetime
# import logging
# 
# LOG_LEVEL = logging.INFO
# 
# DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
# 
# LOG_FORMAT: str = (
#     "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
# )
# logging.basicConfig(
#     level=LOG_LEVEL,
#     format=LOG_FORMAT,
#     datefmt=DATE_FORMAT,
# )
# logger = logging.getLogger(__name__)
# app = FastAPI()
# 
# 
# @app.middleware("http")
# def add_process_time(
#     request: Request,
#     call_next,
# ):
#     start = datetime.time()
#     logger.info(
#         "Метод %s, путь %s",
#         request.method,
#         request.url.path,
#     )
#     response = call_next(request)
#     end_time = time.time() - start
#     logger.info(
#         "Время выполнения запроса %s",
#         end_time,
#     )
#     response.headers["Process-Time"] = end_time
#     return response

```
11. Валидация данных через Pydantic
Объясни, как использовать Pydantic для валидации 
данных в FastAPI. Как добавить ограничения на поля? 
Как создать кастомные валидаторы?

Для валидации данных используем библиотеку Pydantic
При определении класса наследуемся от класса BaseModel
перечисляем поля для пользовательского класс и указываем 
тип для полей

Для реализации кастомной проверки используем декоратор field_validator

```python
import re
from pydantic import (
    BaseModel,
    field_validator,
)
from typing import (
    Annotated,
)

from annotated_types import (
    Len,
    MaxLen,
    Ge,
    MinLen,
)


class Product(BaseModel):
    # валидация на целочисленное значение, больше или равно 1
    id: Annotated[
        int,
        Ge(1),
    ]
    # валидация на строку с миним 3 и максим 50 символов
    name: Annotated[
        str,
        MinLen(3),
        MaxLen(50),
    ]
    # валидация на целочисленное значение и значение больше или равно 0
    stock: Annotated[
        int,
        Ge(0),
    ]

    @field_validator("name")
    @classmethod
    def name_must_be_alpha(cls, v: str):
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s]+$", v):
            raise ValueError("Название должно содержать только буквы")
        return v

```
12.
JWT аутентификация (10 баллов)

Объясни, как реализовать JWT аутентификацию в FastAPI. 
Как создать токен? 
Как проверить токен? Как защитить endpoints?
```python

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Настройте секретный ключ, алгоритм шифрования и другие константы:
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 2) Создайте схему для данных пользователя:
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    
# 3)Настройте OAuth2 пароля для аутентификации и создайте функцию для создания токена:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
Создайте функцию для проверки токена и получения данных пользователя:


Apply
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid token data")
        return TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
Создайте эндпоинт для аутентификации и получения токена:


Apply
app = FastAPI()

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Здесь должна быть логика проверки учетных данных пользователя
    # Например, сравнение с базой данных
    user = {"username": form_data.username}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
Защитите эндпоинты с помощью зависимости для проверки токена:


Apply
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token)

@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
```
12.
JWT аутентификация (10 баллов)

Объясни, как реализовать JWT аутентификацию в FastAPI.
Как создать токен? Как проверить токен?
Как защитить endpoints?

Реализация JWT (JSON Web Token) .
1. Создание токена
Сначала создаем jwt токен таким образом.
Пользователь  вводит логин и пароль, сервер генерирует JWT. 
Формируемо словарь с данными пользователя  и временем когда истечет срок токена exp.
Эти данные кодируются с использованием секретного ключа (SECRET_KEY) и алгоритма хеширования (HS256) можно выбрать и другой вариант.
Далее возвращаем клиенту строку, которую он будет сохранять и прикреплять к каждому запросу.
2. Защита Endpoints (Маршрутов)
Для ограничения доступа к функциям, в FastAPI используем механизм Depends 
Создаем объект OAuth2PasswordBearer, то есть где именно искать токен (обычно в заголовке Authorization: Bearer token).
Этот объект передается как зависимость в те функции, которые мы хотим защитить.
Если токена в запросе нет, FastAPI автоматически вернет ошибку 401 Unauthorized.(в зависимости установлен ли параметр для auto_error = True или False)
3. Проверка токена
Когда в маршрут приходит запрос, то  срабатывает логика проверки внутри зависимости:
Декодирование: пытаемся расшифровать токен,
используя тот же секретный ключ. Если ключ не совпадает, поднимается исключение.
Проверка срока действия: Проверяется поле exp. Если время истекло, токен считается недействительным.
Получение пользователя: Если токен валиден, из него извлекается id пользователя.
Затем сервер идет в базу данных, чтобы убедиться, что такой пользователь всё еще существует.
Передача данных: Если всё в хорошо, то данные пользователя передаются в функцию маршрута.
4. Итоговая схема взаимодействия
Пользователь отправляет POST-запрос с формой логина.
Сервер проверяет пароль и возвращает токен.
браузер сохраняет токен и отправляет его в заголовке при обращении к API.
Зависимость в FastAPI перехватывает запрос, проверяет подпись токена и дает доступ для запроса к коду функции, если все нормально.
# ----------------------------------------------------------
13.
Работа с внешними API (10 баллов)

Объясни, как работать с внешними API в Python. 
Как обрабатывать ошибки? Как реализовать retry-логику? 
В чем разница между requests и aiohttp?

Что бы настроить работу с внешними API для начала нужно
посмотреть как взаимодействовать с этим API, каким образом
отправлять запрсы и какие данные возвращет сервер API.
Нужно ли получить api-key или нет.

При отправке запросов мы можем получить ошибки, которые 
могут быть на стороне сервера и проблемы соединения
Проверяем код ответа сервера или вызываем метод raise_for_status() для поднятия
исключения если получили ошибку. 
Можем получить такие ошибки: Timeout - долгий ответ сервера
ConnectionError - нет интернета, нет нужного адреса
HTTPError - 404 Not found

Retry - повторные попытки запроса через 
экспоненциальнy задержкy(1,2,4,8..) если сервер почему то сразу не ответил
Если мы будем бомбить сервер запрсами, то наш IP просто заблокирую на время


requests синхронная отправка запросов(отправлеяем запрос, пока не получим ответ, код блокируется):
При отправке 1000 запросов, они будут отправлятя по одной. 
aiohttp асинхронная отправка запросов(запросы помещаются в пул запросов и отправляются асинхрнооно, то есть 
пока ждем ответа от сервера мы не блокируем поток а отправляем следующий запрос)
При отправке 1000 запросов одновременно время получения ответа будет равнятся вермени самого долго запроса

# -----------------------------------------------------------

Микросервисная архитектура (10 баллов)

Объясни принципы микросервисной архитектуры. 
Как проектировать микросервисы? 
Как организовывать взаимодействие между сервисами?

Микросервисная архитектура - это написание приложений в котором
создаются отдельные сервисы которые решают только определенные
задачи, только для них характерные(Например сервис для работы с продуктами, заказами, пользователи)
При этом для каждый микросервис разворачивается отдельно, что бы при сбое одного сервиса
другие продолжали работать и что бы можно было мыстро найти и решить проблему.
Так же для каждого микросервиса используется своя база данных

Проектирование микросервиса:
Каждый микросервис определен в своем каталоге и где для данного 
сервиса определены каталоги с представлениями, моделями, базой данных, и настройками 
конфигурации для работы и для развертывания, бизнес логикой для взамиодействия с другими сервисами. 
Ну и конечно модуль для тестирования микросервиса.
И так для каждого микросервиса.

Взаимодействие микросервисов происходит через запросы к данным сервисам через HTTP API
отправляем запрос к сервису заказа, тот присылает ответ и уже данный ответ используем для 
создания платежки. 


15.
Системный дизайн (10 баллов)

Объясни основы системного дизайна. 
В чем разница между вертикальным и 
горизонтальным масштабированием? 
Как использовать кэширование для оптимизации 
производительности?

Системный дизайн - это построение такого приложения, которое
может выдержать высокие нагрузки и не упасть. 

В чем разница между вертикальным и горизонтальным масштабированием
Вертикальное масштабирование - это добавление доплнительных мощностей 
что бы обрабатывать большее количество запросо за счет увеличения ram и cpu
для одного сервера. Если сервер упал, значит все приложение легло

Горизонтальное масштабирование - добавление дополнительных серверов 
и таким образом мы размазываем нагрузку между серверами с использованием балансировщика

Как использовать кеширование для оптимизации:
Кеширование - временное хранение данных для быстрого доступа.
Для оптимизации можем испоьзовать кеш на уровне браузера указывая время хранения полученызх
данных от сервера.
Второй вариант это кеширование на стороне бекенда в базе Redis
