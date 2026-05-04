import os
from pathlib import Path

from pymongo import MongoClient
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


class LogService:
    def __init__(
        self,
        mongo_url=os.getenv("MONGO_URL"),
        db_name="sfmshop",
    ):
        self.client = MongoClient(mongo_url)  # объект клиента для монго
        self.db = self.client[db_name]  # база с именем sfmshop
        self.log_collection = self.db["logs"]  # таблица где будут хранится логи

    def save_order_logs(
        self,
        order_ids: list[int],
        status: str,
    ):
        messages: dict = {
            "order_ids": order_ids,
            "status": status,
            "timestamp": datetime.utcnow(),
        }
        self.log_collection.insert_one(
            document=messages,
        )

    def log_error(
        self,
        message: str,
        stack_trace: Optional[str] = None,
    ):
        """Логировать ошибку"""
        # собираем значения в словать и вставляем в коллекцию logs
        log_entry = {
            "type": "error",
            "message": message,
            "stack_trace": stack_trace,
            "timestamp": datetime.utcnow(),
        }
        # вставляем одно значения используя метод insert_one
        self.log_collection.insert_one(
            log_entry,
        )

    def log_access(
        self,
        ip: str,
        endpoint: str,
        method: str,
        status_code: int,
    ):
        """Логировать доступ"""
        # собираем данные в словарь и добавим как один элемент
        log_entry = {
            "type": "access",
            "ip": ip,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "timestamp": datetime.utcnow(),
        }
        self.log_collection.insert_one(
            log_entry,
        )

    def get_errors(
        self,
        since: Optional[datetime] = None,
    ):
        # задаем ключ для поиска(ищем логи с ошибками)
        query: dict = {"type": "error"}
        # если пришло время, то в запрос включаю поиск диапазона
        # от какого времения брать логи
        if since:
            query["timestamp"] = {"$gte": since}
        return list(self.log_collection.find(query))


log_mongo_service = LogService()
