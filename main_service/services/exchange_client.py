import logging
from typing import Optional, List


import requests
import time
from requests.exceptions import (
    RequestException,
    Timeout,
    ConnectionError,
)

logger = logging.getLogger(__name__)


class MultiExchangeClient:
    """Клиент для работы с API курсов валют"""

    def __init__(
        self,
        base_url: List[str],
    ):
        self.base_urls = base_url  # 4 пункт установка списка маршрутов в атрибут объект
        self.timeout = 5
        self.max_retries = 3

    def get_exchange_rate(
        self,
        base_currency: str,
        target_currency: str,
    ) -> Optional[float]:
        """Получить курс валют с обработкой ошибок и retry"""
        for url in self.base_urls:  # 1 пункт прохождение по API
            for attempt in range(self.max_retries):
                try:
                    logger.info("Получение данных из ресурса %s", url)
                    response = requests.get(
                        f"{url}/{base_currency}",
                        timeout=self.timeout,
                    )
                    if response.status_code == 200:  # Проверка успешности запроса
                        data = response.json()
                        logger.info("Данные успешно получены: %s", data)

                        if target_currency in data.get("conversion_rates", {}):
                            return data["conversion_rates"][target_currency]
                        else:
                            logger.info("Валюта %s  не найдена", target_currency)
                            # 5 если валюта не найдена, запрос к следующему API
                            # 2 пункт Убрал None что бы не выходить из цикла если если нет валюты
                except (Timeout, ConnectionError) as e:
                    logger.info("Обработка ошибки")
                    self.handle_network_error(e, attempt)

                except RequestException as e:
                    logger.info("Ошибка запроса %s", e)
        return None  # Если ни один URL не вернул результат

    def handle_network_error(self, error, attempt):
        """Метод для обработки Timeout и ConnectionError"""
        delay = 2**attempt
        if attempt < self.max_retries - 1:
            print(f"{error}, повтор через {delay}")
            time.sleep(delay)
        else:
            logger.info("Превышено время ожидания после всех попыток")

    def convert_price(
        self,
        price: float,
        from_currency: str,
        to_currency: str,
    ) -> Optional[float]:
        """Конвертировать цену из одной валюты в другую"""
        if from_currency == to_currency:
            return price
        rate = self.get_exchange_rate(
            from_currency,
            to_currency,
        )
        if rate is None:
            return None
        return price * rate


if __name__ == "__main__":
    # Использование
    API_KEY = "your-api-key"  # Замените на реальный ключ
    client = MultiExchangeClient(
        [
            f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest",
            f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest",
            f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest",
        ]
    )
    converted_price = client.convert_price(
        1000,
        "USD",
        "RUB",
    )
    if converted_price:
        print(f"1000 USD = {converted_price}")
    else:
        print("Не удалось получить курс валют")
