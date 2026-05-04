import asyncio
import time
import traceback

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
import aiohttp
from starlette import status

from database.models import Order


async def process_order(order_id: int):
    """Асинхронная обработка заказа"""
    await asyncio.sleep(0.1)  # замираем на указанное время
    print(f"Заказ с id={order_id} обработан")  # выводими информацию
    return {
        "id": order_id,
        "status": "completed",
    }


async def process_orders_async(order_ids: list[int]):
    """Параллельная обработка заказов"""
    start_time = time.time()  # начальное время
    tasks = [
        process_order(ord_id) for ord_id in order_ids
    ]  # список корутин для запуска
    results = await asyncio.gather(
        *tasks,
    )  # запуск паралельно списка корутин в цикле событий
    end_time = time.time()  # время завершения выполнения обработки заказов
    print(
        f"Время выполнения обработки заказов: {end_time-start_time} сек",
    )  # вывод информации
    return results  # возврат результата


def process_order_sync(order_id: int):
    """Синхронная обработка заказов"""
    time.sleep(0.1)  # замираем на указанное время
    print(f"Заказ с id={order_id} обработан")  # выводими информацию


def process_orders_sync(order_ids: list):
    """Синхронная обработка заказов"""
    start_time = time.time()
    for ord_id in order_ids:
        process_order_sync(order_id=ord_id)
    end_time = time.time()
    print(f"Время выполнения синхронного кода: {end_time - start_time}")


async def main():
    order_ids = list(range(1, 101))  # 100 заказов

    # Асинхронная обработка
    start = time.time()
    await process_orders_async(order_ids)
    end = time.time()
    print(f"Асинхронная обработка: {end - start} секунд")


# 2. Интеграция с проектом
async def process_order_with_class(order_id):
    """Асинхронная обработка заказа с использованием класса"""
    try:
        # получение заказа имитация
        await asyncio.sleep(0.1)
        order = Order(
            id=order_id,
            total=3,
            status="pending",
            user_id=1,
        )
        order.status = "completed"
        return order
    except Exception as e:
        print(f"Ошибка при обработке заказа {order_id}: {e}")
        return None


# 3. Асинхронные HTTP-запросы
async def fetch_order_details_async(order_id: int):
    """Получить дополнительные данные и внешнего API"""
    try:
        async with aiohttp.ClientSession() as session:
            url = "http://127.0.0.1:8000/orders/1/"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
    except Exception as e:
        print(f"Ошибка при запросе данных для заказа: {order_id}:{e}")
        return None


# 4. Интеграция с FastAPI
app = FastAPI()
from services.log_mongo_service import log_service  # импортируем объект для сохранеия логов в базу


# данный код должен быть в файле main.py
@app.post("/orders/process/")
async def process_orders_endpoint(
    orders_id: list[int],
    background_tasks: BackgroundTasks,
):
    """Endpoint обработки заказов"""
    if not orders_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет id заказов",
        )
    try:
        # Асинхронная обработка заказов
        results = await process_orders_async(orders_id)

        background_tasks.add_task(
            log_service.save_order_logs,
            orders_id,
            "success",
        )
        return {
            "status": "success",
            "processed": len(results),
            "results": results,
        }
    except Exception as e:
        background_tasks.add_task(
            log_service.log_error,
            message=str(e),
            stack_trace=traceback.format_exc(),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сервера : {e}",
        )


@app.post("/orders/process-background")
async def process_orders_background(
    order_ids: list[int],
    background_tasks: BackgroundTasks,
):
    """Endpoint для фоновой обработки заказов"""
    background_tasks.add_task(
        process_orders_async,
        order_ids,
    )
    background_tasks.add_task(
        log_service.save_order_logs,
        order_ids,
    )
    return {
        "status": "accepted",
        "message": "Обработка заказов запущена в фоне",
    }


if __name__ == "__main__":
    order_ids = list(range(1, 101))  # 100 заказов
    asyncio.run(main())
    print("--" * 30)
    process_orders_sync(order_ids)
    # 2
    result = asyncio.run(process_order_with_class(1))
    print(result)
    # 3
    res = asyncio.run(fetch_order_details_async(1))
    print(res)
    # 4
    uvicorn.run(app, host="127.0.0.1", port=8000)
