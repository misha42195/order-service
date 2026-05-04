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

    def test_five_percent_discount_1000_to_4999(self):
        """Тест: скидка 5% для заказов от 1000 до 4999"""
        assert calculate_discount(Decimal("1000")) == Decimal("50")  # 1000 * 0.05
        assert calculate_discount(Decimal("2500")) == Decimal("125")  # 2500 * 0.05
        assert calculate_discount(Decimal("4999")) == Decimal("249.95")

    def test_ten_percent_discount_5000_to_9999(self):
        """Тест: скидка 10% для заказов от 5000 до 9999"""
        assert calculate_discount(Decimal("5000")) == Decimal("500")  # 5000 * 0.10
        assert calculate_discount(Decimal("7500")) == Decimal("750")  # 7500 * 0.10
        assert calculate_discount(Decimal("9999")) == Decimal("999.9")

    def test_fifteen_percent_discount_10000_and_above(self):
        """Тест: скидка 15% для заказов от 10000 и выше"""
        assert calculate_discount(Decimal("10000")) == Decimal("1500")  # 10000 * 0.15
        assert calculate_discount(Decimal("20000")) == Decimal("3000")  # 20000 * 0.15
        assert calculate_discount(Decimal("100000")) == Decimal(
            "15000"
        )  # 100000 * 0.15

    def test_boundary_1000_exactly(self):
        """Тест: граничная сумма ровно 1000 получает 5% скидку"""
        assert calculate_discount(Decimal("1000")) == Decimal("50")

    def test_boundary_5000_exactly(self):
        """Тест: граничная сумма ровно 5000 получает 10% скидку"""
        assert calculate_discount(Decimal("5000")) == Decimal("500")

    def test_boundary_10000_exactly(self):
        """Тест: граничная сумма ровно 10000 получает 15% скидку"""
        assert calculate_discount(Decimal("10000")) == Decimal("1500")

    def test_negative_price_raises_error(self):
        """Тест: отрицательная сумма заказа вызывает ValueError"""
        with pytest.raises(ValueError):
            calculate_discount(Decimal("-100"))

    def test_string_input_converted(self):
        """Тест: строковый ввод корректно конвертируется в Decimal"""
        assert calculate_discount("10000") == Decimal("1500")

    def test_int_input_converted(self):
        """Тест: целочисленный ввод корректно конвертируется в Decimal"""
        assert calculate_discount(10000) == Decimal("1500")

    def test_float_input_converted(self):
        """Тест: float ввод корректно конвертируется в Decimal"""
        assert calculate_discount(10000.0) == Decimal("1500")

    def test_decimal_precision(self):
        """Тест: результат имеет тип Decimal"""
        result = calculate_discount(Decimal("3333.33"))
        assert isinstance(result, Decimal)
        expected = Decimal("3333.33") * Decimal("0.05")
        assert result == expected


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


# ============== Tests for External Dependency (requests) ==============


@patch("utils.calculations.requests.get")
def test_function_with_external_dependency(mock_get):
    """Тест функции с внешней зависимостью requests.get."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"conversion_rates": {"RUB": 92.5, "EUR": 0.95}}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = get_converted_amount(100, "RUB")

    assert result == 9250.0
    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("utils.calculations.requests.get")
def test_external_api_handles_invalid_currency(mock_get):
    """Тест: неподдерживаемая валюта возвращает None."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"conversion_rates": {"RUB": 92.5}}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = get_converted_amount(100, "XYZ")

    assert result is None
    mock_get.assert_called_once()


@patch("utils.calculations.requests.get")
def test_external_api_raises_on_http_error(mock_get):
    """Тест: HTTP ошибка пробрасывается."""
    mock_get.side_effect = Exception("API unavailable")

    with pytest.raises(Exception):
        get_converted_amount(100, "RUB")
