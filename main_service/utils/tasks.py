import logging
import time

log = logging.getLogger(__name__)


def send_confirm_email(
    order_id: int,
    email: str,
) -> None:
    """Отправка подтверждения пользователю"""
    log.info("Начало отправки письма")
    try:
        time.sleep(3)
        print("Имитация отправки сообщения пользователю")
        log.info(
            "Письмо для заказа %s успешно отправлено на %s",
            order_id,
            email,
        )
    except Exception as e:
        log.error(
            "Ошибка при отправке письма %s",
            e,
        )


task_statuses: dict[str, dict] = {}


def export_catalog(
    task_id: str,  # id для фиксирования задачи в словаре
):
    """Имитация экспрорта каталога"""
    try:  # попытаемся
        # сохраняем в словарь задачу по его ключу и устанавливаем ключи:значения
        task_statuses[task_id] = {"status": "in_process"}
        log.info("Задача %s на экспорт каталога", task_id)
        # имитация долгой работы формирования файла
        time.sleep(5)

        task_statuses[task_id] = {
            "status": "completed"
        }  # меняем статус(информацию о задаче)
        log.info("Задача %s успешно завершена", task_id)

    except Exception as e:  # если получили ошибку в процессе формирования файла
        log.error("Ошибка в задаче %s: %s", task_id, e)  # логируем ошибку в терминал
        task_statuses[task_id] = {
            "status": f"failed:{e}",
        }  # фиксируем свойства задачи в словарь
