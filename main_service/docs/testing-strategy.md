### Какой у тебя подход к тестированию?
 - Я пишу тесты к функциям, методам, и классам
которые относятся к бизенсовым задачам, обрабатывают критически
важные бизнес логику. Сначала подготавливаю данные для тестирования,
далее выполняю действия тестируемого кода и проверяю результат черз assert
- Каждый тест должен быть независимым от других.
- Давать осмысленные названия для тестов.
### Какие типы тестов ты пишешь?
 - Я пишу модульные тесты для функций, методов и классов
 - Пишу интеграционные тесты для тестирования API и базы данных
Использую unittest.mock для изоляции данных и внешних API 
 - Интеграционные тесты. Здесь проверяю настоящие запросы
к приложению которе работает с реальной базой или базой запущенной
через Docker(Проверка кодов ответа, содержимое json ответа, и данные из БД)
Примеры тестов
```python
from unittest.mock import patch, MagicMock

import pytest
from decimal import Decimal

from utils.calculations import (
    calculate_delivery,
    calculate_discount,
    get_converted_amount,
)

# ============== Фикстуры ==============


@pytest.fixture
def order_total():
    """Создает Decimal сумму заказа 10000"""
    return Decimal("10000")


@pytest.fixture
def order_totals():
    """Создает список сумм заказов для параметризации"""
    return [
        Decimal("0"),
        Decimal("500"),
        Decimal("1000"),
        Decimal("5000"),
        Decimal("10000"),
        Decimal("50000"),
    ]


# ============== calculate_discount Tests ==============


class TestCalculateDiscount:
    """Тесты для функции расчета скидки"""

    def test_no_discount_below_1000(self):
        """Тест: заказы меньше 1000 не получают скидку"""
        assert calculate_discount(Decimal("0")) == Decimal("0")
        assert calculate_discount(Decimal("500")) == Decimal("0")
        assert calculate_discount(Decimal("999")) == Decimal("0")



    def test_boundary_1000_exactly(self):
        """Тест: граничная сумма ровно 1000 получает 5% скидку"""
        assert calculate_discount(Decimal("1000")) == Decimal("50")



    def test_string_input_converted(self):
        """Тест: строковый ввод корректно конвертируется в Decimal"""
        assert calculate_discount("10000") == Decimal("1500")


@pytest.mark.parametrize(
    "order_total,expected_discount",
    [
        (Decimal("0"), Decimal("0")),
        (Decimal("500"), Decimal("0")),
        (Decimal("999"), Decimal("0")),
        (Decimal("1000"), Decimal("50")),
        (Decimal("2500"), Decimal("125")),
        (Decimal("4999"), Decimal("249.95")),
        (Decimal("5000"), Decimal("500")),
        (Decimal("7500"), Decimal("750")),
        (Decimal("9999"), Decimal("999.9")),
        (Decimal("10000"), Decimal("1500")),
        (Decimal("20000"), Decimal("3000")),
        (Decimal("100000"), Decimal("15000")),
    ],
)
def test_calculate_discount_parametrized(order_total, expected_discount):
    """Тест: параметризованный тест расчета скидки для всех порогов"""
    assert calculate_discount(order_total) == expected_discount


@pytest.mark.parametrize(
    "weight,distance,expected_result",
    [
        (1, 1, 120),  # 100 + 1*10 + 1* 10 = 120
        (5, 5, 200),  # 100 + 5*10 + 5* 10 = 200
        (15, 15, 400),  # 100 + 15*10 + 15*10 = 400
    ],
)
def test_calculate_delivery(
    weight,
    distance,
    expected_result,
):
    """Тест: расчет доставки для разных случаев"""
    assert calculate_delivery(weight, distance) == expected_result


@patch("utils.calculations._get_cached_rates")
def test_get_converted_amount_success(mock_rates):
    """Тест успешной конвертации валюты."""
    mock_rates.return_value = {"RUB": 85.5, "EUR": 0.92}

    result = get_converted_amount(10, "RUB")

    assert result == 855.0
    mock_rates.assert_called_once()


@patch("utils.calculations._get_cached_rates")
def test_get_converted_amount_unsupported_currency(mock_rates):
    """Тест конвертации в неподдерживаемую валюту."""
    mock_rates.return_value = {"RUB": 85.5, "EUR": 0.92}

    result = get_converted_amount(10, "GBP")

    assert result is None


@patch("utils.calculations._get_cached_rates")
def test_get_converted_amount_zero_amount(mock_rates):
    """Тест конвертации нулевой суммы."""
    mock_rates.return_value = {"RUB": 85.5}

    result = get_converted_amount(0, "RUB")

    assert result == 0.0
```
### Какое покрытие кода? 
 - Покрытие кода тестами должно быть более 80%
 - Для функций и методов под 100%
 - Интеграционные тесты (API и БД) > 70%
### Как ты используешь моки?
 - Я использую моки что бы тестировать код запросов 
к API и взаимодействия с БД. Что бы избежать долгого ответа от API
и БД и избежать ошибок взаимодействия с ними я мокирую данные то
есть создаю изолированние данные. При этом происходит подмена мокированных
данные на реальные из базы. 
### Что такео TDD
 - Это стратегия разработки Test Driver Develop - 
Написание кода через тестирование. 
Сначала пишется код теста, который проваливается так как код функции еще 
не реализован(красный этап)
 - Далее пишется минимальный код теста который проходит(зеленый этап)
 - Далее пишется код функции и рефакторится(этап рефакторинга)
