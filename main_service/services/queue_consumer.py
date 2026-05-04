import json
import logging
import time

import pika
from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel

from services import (
    update_stock,
    generate_report,
)
from services.tasky_services import send_email

log = logging.getLogger(__name__)


class QueueConsumer:
    """Consumer для обработки задач из очереди rabbitmq"""

    def __init__(
        self,
        host: str = "localhost",
    ):
        self.host: str = host
        self.connection: BlockingConnection | None = None
        self.channel: BlockingChannel | None = None
        self.max_retry: int = 5

    def connect(self):
        """Подключение к rabbitmq"""
        try:
            self.connection = pika.BlockingConnection(
                parameters=pika.ConnectionParameters(self.host)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(
                "order_create_processing",
                durable=True,
            )
            self.channel.queue_declare(
                queue="order_create_processing_errors",
                durable=True,
            )
            self.channel.basic_qos(prefetch_count=1)
            return True
        except Exception as e:
            log.info("Ошибка подключения к rabbitmq %s", e)
            return False

    def process_message(self, ch, method, properties, body):
        """Обработка сообщений из очереди"""
        retry_count = 0
        try:
            # Безопасное получение заголовков
            if properties and properties.headers:
                retry_count = properties.headers.get("x-retry-count", 0)

            message = json.loads(body)
            task = message.get("task")
            order_id = message.get("order_id")

            if task == "send_email":
                email = message.get("email")
                send_email(order_id, email)
            elif task == "update_stock":
                update_stock(order_id)
            elif task == "generate_report":
                generate_report(order_id)
            else:
                log.warning("Получена неизвестная задача %s", task)

            # ИСПРАВЛЕНО: только delivery_tag
            ch.basic_ack(delivery_tag=method.delivery_tag)
            log.info("Задача %s для заказа %s обработана", task, order_id)

        except Exception as e:
            log.error("Ошибка обработки задачи: %s", e)

            if retry_count < self.max_retry:
                retry_count += 1
                delay = 2**retry_count

                log.info(
                    "Повторная попытка %s / %s через %s сек",
                    retry_count,
                    self.max_retry,
                    delay,
                )
                time.sleep(delay)

                ch.basic_publish(
                    exchange="",
                    routing_key="order_create_processing",
                    body=body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        headers={"x-retry-count": retry_count},
                    ),
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                ch.basic_publish(
                    exchange="",
                    routing_key="order_create_processing_errors",
                    body=body,
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                log.info(
                    "Задача отправлена в очередь ошибок после %s попыток",
                    self.max_retry,
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        """Запуск сообщений"""
        if not self.connect():
            return
        self.channel.basic_consume(
            queue="order_create_processing",
            on_message_callback=self.process_message,
        )
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.close()

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()


def run_worker():
    consumer = QueueConsumer(host="localhost")
    consumer.start_consuming()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    consumer = QueueConsumer(host="localhost")
    consumer.start_consuming()
