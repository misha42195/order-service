import pytest
from pydantic import ValidationError

from models.product import Product, ProductBase, ProductCreate, ProductResponse
from models.user import User, UserCreate
from models.order import Order, OrderCreate, OrderPatchUpdate
from models.exeptions import InvalidOrderError, NegativePriceError, InsufficientStockError


# ============== Фикстуры ==============

@pytest.fixture
def simple_user():
    """Создает тестового пользователя"""
    return User(name="Misha", email="misha@gmail.com")


@pytest.fixture
def product():
    """Создает один тестовый товар: монитор, цена 1000, количество 10"""
    return Product(name="монитор", price=1000, quantity=10)


@pytest.fixture
def list_products():
    """Создает список из двух тестовых товаров:
    - монитор: цена 1000, количество 10 (итого 10000)
    - принтер: цена 5000, количество 5 (итого 25000)
    Общая сумма заказа: 35000
    """
    return [
        Product(name="монитор", price=1000, quantity=10),
        Product(name="принтер", price=5000, quantity=5),
    ]


@pytest.fixture
def user_pydantic():
    """Создает тестового пользователя через Pydantic модель UserCreate"""
    return UserCreate(name="Misha", email="misha@gmail.com", password="secret123", balance=1000.0)


# ============== Product Tests ==============

class TestProductClass:
    """Тесты для класса Product (OLD_PRODUCT_MODEL)"""

    def test_create_product(self, product):
        """Тест: создание товара с корректными данными"""
        assert product.name == "монитор"
        assert product.price == 1000
        assert product.quantity == 10

    def test_get_total_price(self, product):
        """Тест: расчет общей стоимости товара (цена * количество)"""
        assert product.get_total_price() == 10000

    def test_negative_price_raises_error(self):
        """Тест: создание товара с отрицательной ценой вызывает NegativePriceError"""
        with pytest.raises(NegativePriceError):
            Product(name="товар", price=-100, quantity=5)

    def test_sell_success(self, product):
        """Тест: успешная продажа товара уменьшает количество на складе"""
        product.sell(3)
        assert product.quantity == 7

    def test_sell_insufficient_stock(self, product):
        """Тест: продажа большего количества, чем есть на складе, вызывает InsufficientStockError"""
        with pytest.raises(InsufficientStockError):
            product.sell(15)

    def test_sell_exact_amount(self, product):
        """Тест: продажа точного количества товара"""
        product.sell(10)
        assert product.quantity == 0

    def test_product_str(self, product):
        """Тест: строковое представление товара"""
        assert "монитор" in str(product)
        assert "1000" in str(product)
        assert "10" in str(product)

    def test_product_repr(self, product):
        """Тест: repr представление товара"""
        assert "монитор" in repr(product)
        assert "1000" in repr(product)
        assert "10" in repr(product)

    def test_product_eq(self):
        """Тест: сравнение двух одинаковых товаров"""
        p1 = Product(name="монитор", price=1000, quantity=10)
        p2 = Product(name="монитор", price=1000, quantity=5)
        assert p1 == p2

    def test_product_ne(self):
        """Тест: сравнение двух разных товаров"""
        p1 = Product(name="монитор", price=1000, quantity=10)
        p2 = Product(name="принтер", price=5000, quantity=5)
        assert p1 != p2

    def test_product_lt(self):
        """Тест: сравнение товаров по цене (меньше)"""
        p1 = Product(name="монитор", price=1000, quantity=10)
        p2 = Product(name="принтер", price=5000, quantity=5)
        assert p1 < p2


class TestProductPydantic:
    """Тесты для Pydantic моделей Product"""

    def test_product_base_valid(self):
        """Тест: создание ProductBase с валидными данными"""
        product = ProductBase(name="Телевизор", price=500.0, stock=20)
        assert product.name == "Телевизор"
        assert product.price == 500.0
        assert product.stock == 20

    @pytest.mark.parametrize("price", [0, 0.5, -10])
    def test_product_base_invalid_price(self, price):
        """Тест: цена должна быть >= 1 (параметризация: 0, 0.5, -10)"""
        with pytest.raises(ValidationError):
            ProductBase(name="Товар", price=price, stock=10)

    @pytest.mark.parametrize("stock", [-1, -100])
    def test_product_base_invalid_stock(self, stock):
        """Тест: stock должен быть >= 0 (параметризация: -1, -100)"""
        with pytest.raises(ValidationError):
            ProductBase(name="Товар", price=100, stock=stock)

    def test_product_base_name_too_short(self):
        """Тест: name должен быть не короче 3 символов"""
        with pytest.raises(ValidationError):
            ProductBase(name="ab", price=100, stock=10)

    def test_product_base_name_too_long(self):
        """Тест: name должен быть не длиннее 100 символов"""
        with pytest.raises(ValidationError):
            ProductBase(name="a" * 101, price=100, stock=10)

    def test_product_create_valid(self):
        """Тест: создание ProductCreate с валидными данными"""
        product = ProductCreate(name="  Телевизор  ", price=500.0, stock=20)
        assert product.name == "Телевизор"  # name должен быть обрезан

    def test_product_create_empty_name(self):
        """Тест: пустое имя после trim вызывает ошибку"""
        with pytest.raises(ValidationError):
            ProductCreate(name="   ", price=100, stock=10)


class TestProductResponse:
    """Тесты для ProductResponse"""

    def test_product_response_valid(self):
        """Тест: создание ProductResponse с валидными данными"""
        response = ProductResponse(id=1, name="Товар", price=100.0, stock=10)
        assert response.id == 1
        assert response.price == 100.0

    def test_product_response_negative_price(self):
        """Тест: negative price в ответе вызывает ValidationError"""
        with pytest.raises(ValidationError):
            ProductResponse(id=1, name="Товар", price=-50.0, stock=10)


# ============== User Tests ==============

class TestUserClass:
    """Тесты для класса User (OLD_USER_MODEL)"""

    def test_create_user(self, simple_user):
        """Тест: создание пользователя"""
        assert simple_user.name == "Misha"
        assert simple_user.email == "misha@gmail.com"

    def test_get_info(self, simple_user):
        """Тест: метод get_info возвращает корректную информацию"""
        info = simple_user.get_info()
        assert "Misha" in info
        assert "misha@gmail.com" in info


class TestUserPydantic:
    """Тесты для Pydantic моделей User"""

    def test_user_create_valid(self, user_pydantic):
        """Тест: создание UserCreate с валидными данными"""
        assert user_pydantic.name == "Misha"
        assert user_pydantic.email == "misha@gmail.com"

    def test_user_create_invalid_email(self):
        """Тест: невалидный email вызывает ValidationError"""
        with pytest.raises(ValidationError):
            UserCreate(name="Misha", email="not-an-email", password="secret")

    def test_user_create_empty_name(self):
        """Тест: пустое имя после trim вызывает ошибку"""
        with pytest.raises(ValidationError):
            UserCreate(name="   ", email="test@test.com", password="secret")

    def test_user_create_name_too_short(self):
        """Тест: имя короче 3 символов вызывает ошибку"""
        with pytest.raises(ValidationError):
            UserCreate(name="Mi", email="test@test.com", password="secret")

    @pytest.mark.parametrize("balance", [0, 100.50, 1000])
    def test_user_create_valid_balance(self, balance):
        """Тест: balance должен быть >= 0 (параметризация)"""
        user = UserCreate(name="Misha", email="test@test.com", password="secret", balance=balance)
        assert user.balance == balance

    def test_user_create_negative_balance(self):
        """Тест: negative balance вызывает ValidationError"""
        with pytest.raises(ValidationError):
            UserCreate(name="Misha", email="test@test.com", password="secret", balance=-100)


# ============== Order Tests ==============

class TestOrderClass:
    """Тесты для класса Order"""

    def test_create_order_with_all_fields(self, simple_user, list_products):
        """Тест: создание заказа со всеми полями"""
        order = Order(user=simple_user, products=list_products, order_id=1)
        assert order.user == simple_user
        assert order.products == list_products
        assert order.order_id == 1
        assert order.total == 35000

    def test_create_order_without_order_id(self, simple_user, list_products):
        """Тест: создание заказа без order_id (по умолчанию None)"""
        order = Order(user=simple_user, products=list_products)
        assert order.order_id is None
        assert order.total == 35000

    def test_calculate_total(self, simple_user, list_products):
        """Тест: расчет стоимости заказа"""
        order = Order(user=simple_user, products=list_products)
        assert order.total == 35000
        assert order.calculate_total() == 35000

    def test_order_str_with_id(self, simple_user, list_products):
        """Тест: строковое представление заказа с ID"""
        order = Order(user=simple_user, products=list_products, order_id=1)
        order_str = str(order)
        assert "Заказ #1" in order_str
        assert "35000" in order_str
        assert "Misha" in order_str

    def test_order_str_without_id(self, simple_user, list_products):
        """Тест: строковое представление заказа без ID"""
        order = Order(user=simple_user, products=list_products)
        order_str = str(order)
        assert "Заказ на сумму" in order_str
        assert "35000" in order_str

    def test_create_order_empty_products_raises_error(self, simple_user):
        """Тест: заказ с пустым списком товаров вызывает InvalidOrderError"""
        with pytest.raises(InvalidOrderError):
            Order(user=simple_user, products=[])

    def test_create_order_none_products_raises_error(self, simple_user):
        """Тест: заказ с None вместо товаров вызывает InvalidOrderError"""
        with pytest.raises(InvalidOrderError):
            Order(user=simple_user, products=None)


class TestOrderPydantic:
    """Тесты для Pydantic моделей Order"""

    def test_order_create_valid(self):
        """Тест: создание OrderCreate с валидными данными"""
        order = OrderCreate(user_id=1, total=1000.0, status="новый")
        assert order.user_id == 1
        assert order.total == 1000.0
        assert order.status == "новый"

    def test_order_create_items(self):
        """Тест: создание OrderCreate со списком товаров"""
        order = OrderCreate(user_id=1, total=1000.0, status="новый", items=[{"product_id": 1, "qty": 2}])
        assert len(order.items) == 1

    @pytest.mark.parametrize("total", [0, 100.5, 10000])
    def test_order_create_valid_total(self, total):
        """Тест: total должен быть >= 0 (параметризация)"""
        order = OrderCreate(user_id=1, total=total, status="новый")
        assert order.total == total

    def test_order_create_negative_total(self):
        """Тест: negative total вызывает ValidationError"""
        with pytest.raises(ValidationError):
            OrderCreate(user_id=1, total=-100.0, status="новый")

    def test_order_create_status_too_short(self):
        """Тест: status короче 3 символов вызывает ошибку"""
        with pytest.raises(ValidationError):
            OrderCreate(user_id=1, total=1000.0, status="но")

    def test_order_create_status_too_long(self):
        """Тест: status длиннее 20 символов вызывает ошибку"""
        with pytest.raises(ValidationError):
            OrderCreate(user_id=1, total=1000.0, status="а" * 21)

    def test_order_patch_update_partial(self):
        """Тест: частичное обновление заказа через PATCH"""
        patch = OrderPatchUpdate(user_id=1, total=500.0, status="обновлен")
        assert patch.total == 500.0
