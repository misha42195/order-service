"""
TDD (Test-Driven Development) - разработка через тестирование,
где тесты пишутся перед кодом.
Цикл красный-зеленый-рефакторинг.

TDD - состоит из трех этапов:
- красный - написать тест, который падает(нет кода)
- зеленый - написать минимальный тест, чтобы тест прошел
- рефакторинг - улучшить код, сохраняя тесты зелеными

"""

from starlette import status

# import pytest
# from starlette import status
#
# from api.main import app
#
# # Красный, написать тест который падает
# from utils.calculations import calculate_delivery
#
#
# @pytest.mark.parametrize(
#     "weight, distance, expected",
#     [
#         (1, 10, 160),
#         (5, 50, 400),
#         (10, 100, 700),
#     ],
# )
# def test_calculate_delivery(
#     weight,
#     distance,
#     expected,
# ):
#     """Тест: расчет стоимости доставки"""
#     # Тест для функции, которой еще нет
#     assert calculate_delivery(weight, distance) == expected
#
#
# # TDD - для проектирования API
# from fastapi.testclient import TestClient
#
# client = TestClient(app=app)
#
#
# def test_create_order_endpoint():
#     """Тест: создание заказа через API"""
#     response = client.post(
#         "/order",
#         json={
#             "user_id": 1,
#             "items": [
#                 {"product_id": 1, "quantity": 2},
#             ],
#         },
#     )
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.json()["id"] is not None

"""
Мок - это объект, который имитирует поведение реального
объекта для тестирования

Стаб - это упрощенная версия объекта, которая возвращает 
предопределенные значения
"""
from unittest.mock import (
    Mock,
    MagicMock,
    patch,
)

mock_db = Mock()
mock_db.execute.return_value = {
    "id": 1,
    "status": "created",
}
result = mock_db.execute("select * from orders")
print(result)

"""
MagicMock - это расширенная версия Mock, которая 
автоматически создает атрибуты.
"""

mock_service = MagicMock()
mock_service.get_user.return_value = {
    "id": 1,
    "name": "Test",
}
mock_service.send_email.return_value = True

# Использование
user = mock_service.get_user()
print(user)

m = MagicMock()
m.__len__.return_value = 5
m.__iter__.return_value = iter(range(5))

print(len(m))
print(list(m))


"""
Практический пример использования
"""
from unittest.mock import MagicMock

mock_cursor = MagicMock()
mock_cursor.__enter__.return_value = mock_cursor
mock_cursor.fetchall.return_value = [
    (1, "Иван"),
    (2, "Петр"),
]

with mock_cursor as cursor:
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# Правильное решение
# testing/test_api.py
from unittest.mock import (
    MagicMock,
)
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


@patch("src.database.connection.execute")
def test_create_order(mock_execute):
    """Тест создания заказа с моком БД"""
    # настройка мока БД
    mock_execute.return_value = {"id": 1, "status": "created"}

    # вызова API
    response = client.post(
        "/orders",
        json={
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 2}],
        },
    )

    # Проверка результата
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == 1

    # Проверка, что БД была вызвана
    mock_execute.assert_called_once()
