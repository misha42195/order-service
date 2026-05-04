# import pytest
# from pydantic import ValidationError, BaseModel
#
# from models.product import (
#     ProductBase,
#     ProductCreate,
#     ProductPatchUpdate,
#     ProductResponse,
#     ProductPutUpdate,
# )
#
#
# class ProductTest(BaseModel):
#     """Вспомогательная модель для тестовых данных"""
#     product_id: int
#     expected_name: str
#     expected_price: float
#     expected_stock: int
#
#
# def test_product_put_update():
#     """Тест полного обновления продукта (PUT)"""
#     update_data = {"name": "Updated Full Name", "price": 99.99, "stock": 10}
#     put_model = ProductPutUpdate(**update_data)
#     assert put_model.name == "Updated Full Name"
#
#
# def test_product_patch_update():
#     """Тест частичного обновления (PATCH)"""
#     patch_data = ProductPatchUpdate(name="New Name")
#     assert patch_data.name == "New Name"
#     assert patch_data.price is None
#
#
# def test_product_response_has_id():
#     """Тест: ProductResponse содержит поле id"""
#     product1 = ProductResponse(id=1, name="Product 1", price=10.99, stock=5)
#     assert product1.id == 1
#     assert product1.name == "Product 1"
#
#
# def test_product_test_model():
#     """Тест: вспомогательная модель ProductTest"""
#     product_test1 = ProductTest(
#         product_id=1,
#         expected_name="Product 1",
#         expected_price=10.99,
#         expected_stock=5,
#     )
#     assert product_test1.product_id == 1
#
#
# def test_product_create_invalid_price():
#     """Тест валидации: цена < 1 в ProductCreate вызывает ошибку"""
#     with pytest.raises(ValidationError):
#         ProductCreate(name="Cheap", price=0.5, stock=10)
#
#
# def test_product_response_valid():
#     """Тест корректного формирования ответа API"""
#     response_data = {
#         "id": 101,
#         "name": "Тестовый товар",
#         "price": 500.0,
#         "stock": 10,
#     }
#     response = ProductResponse(**response_data)
#     assert response.id == 101
#     assert response.name == "Тестовый товар"
#     assert response.price == 500.0
#
#
# def test_product_response_negative_price():
#     """Тест валидатора: цена в ответе не может быть < 0"""
#     with pytest.raises(ValidationError):
#         ProductResponse(id=1, name="Ошибка", price=-100.0, stock=5)
