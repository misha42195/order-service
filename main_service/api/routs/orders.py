import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from starlette import status

from database.models import Order, User
from models.order import OrderCreate

from services.queue_producer import QueueProducer
from database.connection import get_db
from utils.tasks import (
    send_confirm_email,
    task_statuses,
    export_catalog,
)
from services.log_service import log_service

router = APIRouter()
producer = QueueProducer()


# Итоговое задание
@router.post(
    "/orders",
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    log_service.info("Создание заказа", user_id=order_in.user_id)
    new_order = Order(
        total=order_in.total,
        status=order_in.status,
        user_id=order_in.user_id,
    )

    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    log_service.info("Заказ создан", order_id=new_order.id)

    result = await db.execute(
        select(User).where(
            User.id == new_order.user_id,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        log_service.critical("Нет пользователя")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    log_service.info("Пользователь", user_name=user.name)

    # фоновые задачи
    log_service.info("Задача: send emai ")
    producer.send_order_task(
        order_id=new_order.id,
        task_type="send_email",
        data={"email": user.email},
    )
    log_service.info("Задача: update stock")
    producer.send_order_task(
        order_id=new_order.id,
        task_type="update_stock",
        data={},
    )
    log_service.info("Задача: generate report")
    producer.send_order_task(
        order_id=new_order.id,
        task_type="generate_report",
        data={"total": new_order.total},
    )

    return {"order_id": new_order.id, "status": "processing"}


@router.post(
    path="/orders/{order_id}/confirm",
    status_code=status.HTTP_201_CREATED,
)
async def order_confirm(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Отправка подтверждения заказа"""
    query = select(Order).where(Order.id == order_id).options(selectinload(Order.user))
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        log_service.warning("Заказ не существует")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден",
        )
    if not order.user:
        log_service.warning("Заказ без пользователя", order_id=order_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    log_service.info("Запуск фоновой задачи подтверждения")
    background_tasks.add_task(
        send_confirm_email,
        order_id=order_id,
        email=order.user.email,
    )
    return {
        "status": "confirmed",
        "order_id": order_id,
    }


@router.post(
    "/exports",
    status_code=status.HTTP_201_CREATED,
)
async def start_export(
    background_tasks: BackgroundTasks,
):
    """Запуск экспорта"""
    task_id = str(uuid.uuid4())  # создаем id для задачи

    task_statuses[task_id] = {  # формируем словарь с данными
        "status": "pending",
    }

    background_tasks.add_task(
        export_catalog,
        task_id,
    )

    return {
        "task_id": task_id,
        "status": "accepted",
    }


@router.get("/exports/{task_id}")
async def get_export_status(
    task_id: str,  # принимаем id задачи для получения информации
):
    """Получение статуса задачи по id"""
    task = task_statuses.get(task_id)  # получаем задачу из словаря по его id
    if not task:  # если нет задачи то прокидываем ошибку
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Нет задачи по {task_id}",
        )
    return {  # возвращаем информацию по ключам
        "task_id": task_id,
        "status": task.get("status"),
        "result": task.get("result"),
    }
