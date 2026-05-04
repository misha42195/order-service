import logging
from queue import Queue

task_queue: Queue = Queue()
import time

log = logging.getLogger(__name__)


def send_email(order_id: int, email: str) -> None:
    """Имитация отправки email пользователю"""
    log.info("Начало отправки письма для заказа %s на адрес %s", order_id, email)
    time.sleep(2)  # Имитация сетевой задержки SMTP-сервера
    log.info("Письмо для заказа %s успешно отправлено", order_id)


def update_stock(order_id: int) -> None:
    """Имитация обновления остатков на складе"""
    log.info(
        "Обновление остатков для заказа %s.",
        order_id,
    )
    time.sleep(1.5)  # Имитация запросов к базе данных
    log.info("Склад для заказа %s полностью обновлен", order_id)


def notify_manager(order_id: int, total: float) -> None:
    """Имитация уведомления менеджера в Telegram/Slack"""
    log.info("Уведомление менеджера о новом заказе %s на сумму %s", order_id, total)
    time.sleep(0.5)
    log.info("Менеджер уведомлен о заказе %s", order_id)


def generate_report(order_id: int):
    """Имитация создания PDF-отчета"""
    print(f"[WORKER] Генерация отчетности по заказу #{order_id}...")
    time.sleep(2)  # Имитация тяжелой операции
    print(f"[WORKER] Отчет для заказа #{order_id} сформирован и сохранен в хранилище")
