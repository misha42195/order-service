from unittest.mock import (
    AsyncMock,
    patch,
)
from fastapi.testclient import TestClient
from starlette import status

from api.main import app

client = TestClient(app)


@patch("api.routs.products.cache_service.get_products", new_callable=AsyncMock)
def test_get_products(mock_get_products):
    """Тест получения товаров из кэша.

    Мокируем cache_service.get_products() - async метод,
    который возвращает товары из Redis.
    """
    mock_get_products.return_value = [
        {"id": 1, "name": "Product 1", "price": 100},
        {"id": 2, "name": "Product 2", "price": 200},
    ]

    response = client.get("/api/v1/products")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "products" in data
    assert len(data["products"]) == 2
    mock_get_products.assert_called_once()


@patch("api.routs.products.cache_service.get")
@patch("api.routs.products.cache_service.set")
@patch("database.connection.execute")
def test_create_order(
    mock_cache_get,
    mock_cache_set,
    mock_execute,
):
    """Тест создания заказа.

    Мокируем:
    - database.connection.execute - выполнение SQL запросов
    - services.cache_service.get - получение данных из кэша
    """
    # настройка мока БД
    mock_execute.return_value = {
        "id": 2,
        "status": "created",
    }
    # настройка мока кэша
    mock_cache_get.return_value = None
    mock_cache_set.return_value = True
    response = client.post(
        "/orders",
        json={
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 2}],
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == 1
    mock_execute.assert_called_once()
    mock_cache_get.assert_called_once()
