# import pytest
#
# from models.order import Order, InvalidOrderError
# from models.product import Product
# from models.user import User
#
#
# @pytest.fixture
# def simple_user():
#     """Создает тестового пользователя с фиксированными данными"""
#     return User(name="Misha", email="misha@gmail.com")
#
#
# @pytest.fixture
# def list_products():
#     """Создает список из двух тестовых товаров:
#     - монитор: цена 1000, количество 10 (итого 10000)
#     - принтер: цена 5000, количество 5 (итого 25000)
#     Общая сумма заказа: 35000
#     """
#     return [
#         Product(name="монитор", price=1000, quantity=10),
#         Product(name="принтер", price=5000, quantity=5),
#     ]
#
#
# def test_create_order_with_all_fields(simple_user, list_products):
#     """Тест: создание заказа со всеми полями"""
#     order = Order(user=simple_user, products=list_products, order_id=1)
#
#     assert order.user == simple_user
#     assert order.products == list_products
#     assert order.order_id == 1
#     assert order.total == 35000
#
#
# def test_create_order_without_order_id(simple_user, list_products):
#     """Тест: создание заказа без order_id (по умолчанию None)"""
#     order = Order(user=simple_user, products=list_products)
#
#     assert order.user == simple_user
#     assert order.products == list_products
#     assert order.order_id is None
#     assert order.total == 35000
#
#
# def test_calculate_total(simple_user, list_products):
#     """Тест: расчет стоимости заказа"""
#     order = Order(user=simple_user, products=list_products)
#
#     assert order.total == 35000
#     assert order.calculate_total() == 35000
#
#
# def test_create_order_empty_products_raises_error(simple_user):
#     """Тест: заказ с пустым списком товаров вызывает ошибку"""
#     with pytest.raises(InvalidOrderError):
#         Order(user=simple_user, products=[])
#
#
# def test_create_order_none_products_raises_error(simple_user):
#     """Тест: заказ с None вместо товаров вызывает ошибку"""
#     with pytest.raises(InvalidOrderError):
#         Order(user=simple_user, products=None)
