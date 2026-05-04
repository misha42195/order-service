import json
import logging

import pika

log = logging.getLogger(__name__)


class QueueProducer:
    def __init__(self, host: str = "localhost"):
        """Producer для отправки задачи в очередь rabbitmq"""
        self.host = host
        self.connection = None
        self.channel = None

    def connect(self):
        """Подключение"""
        try:
            self.connection = pika.BlockingConnection(
                parameters=pika.ConnectionParameters(self.host),
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(
                queue="order_create_processing",
                durable=True,
            )
            return True
        except Exception as e:
            log.error("Ошибка подключения к RabbitMQ %s", e)
            return False

    def send_order_task(self, order_id: int, task_type: str, data: dict):
        """Отправить задачу на обработку заказа"""
        if not self.channel or self.connection.is_closed:
            if not self.connect():
                return False

        try:
            message = {
                "task": task_type,
                "order_id": order_id,
                **data,
            }

            if self.channel is None:
                log.error("Канал не инициализирован")
                return False

            self.channel.basic_publish(
                exchange="",
                routing_key="order_create_processing",
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )
            log.info("Задача отправлена в очередь: %s", message)
            return True
        except Exception as e:
            log.error("Ошибка отправки задачи: %s", e)
            return False

    def close(self):
        """Закрытие соединения"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            log.info("Соединение Producer закрыто")
