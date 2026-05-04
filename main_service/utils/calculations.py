from decimal import Decimal
from functools import lru_cache

import requests


def calculate_discount(order_total: Decimal) -> Decimal:
    """Рассчитать скидку на основе суммы заказа с использованием Decimal"""
    if not isinstance(order_total, Decimal):
        order_total = Decimal(str(order_total))

    if order_total < 0:
        raise ValueError("Цена не может быть отрицательной")

    # Используем константы или кортежи для гибкости
    if order_total >= Decimal("10000"):
        discount_rate = Decimal("0.15")
    elif order_total >= Decimal("5000"):
        discount_rate = Decimal("0.10")
    elif order_total >= Decimal("1000"):
        discount_rate = Decimal("0.05")
    else:
        discount_rate = Decimal("0")

    return order_total * discount_rate


def calculate_delivery(
    weight: float,
    distance: float,
) -> float:
    """Расчет стоимости доставки от веса и расстояния
    Args:
        weight: вест товара в кг
        distance: расстояние в км

        Return:
             Стоимость доставки в рублях
    """
    base_price = 100
    weight_price = weight * 10
    distance_price = distance * 10
    return base_price + weight_price + distance_price


def get_converted_amount(amount: float, currency: str) -> float | None:
    """Конвертирует сумму из USD в указанную валюту.

    Использует кэширование курсов через lru_cache для оптимизации
    повторных запросов.

    Args:
        amount: Сумма в USD для конвертации.
        currency: Код целевой валюты (например, "RUB", "EUR").

    Returns:
        Конвертированная сумма или None, если валюта не поддерживается.

    Raises:
        requests.HTTPError: При ошибке API запроса.
    """
    rates = _get_cached_rates()
    rate = rates.get(currency)
    if not rate:
        return None
    return amount * rate


@lru_cache(maxsize=128)
def _get_cached_rates() -> dict:
    """Получает и кэширует курсы валют с API.

    Returns:
        Словарь курсов конвертации из API.

    Raises:
        requests.HTTPError: При ошибке API запроса.
    """
    response = requests.get(
        "https://v6.exchangerate-api.com/v6/d523029a0a73b04cb4e3d6fe/latest/USD",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["conversion_rates"]
