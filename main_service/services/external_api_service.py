# реализовать клиента для получения курса валют
import asyncio
import logging
from typing import Optional

import aiohttp

from aiohttp import ClientTimeout
from requests.exceptions import (
    RequestException,
)

logger = logging.getLogger(__name__)


class ExchangeClient:
    def __init__(
        self,
        url: str = "https://v6.exchangerate-api.com/v6/d523029a0a73b04cb4e3d6fe/latest/",
    ):
        self.url = url
        self.max_retry = 3
        self.timeout = ClientTimeout(5)

    async def get_exchange_rate(
        self,
        base_currency: str,
        target_currency: str,
    ):

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            for attempt in range(self.max_retry):
                try:
                    async with session.get(f"{self.url}{base_currency}") as response:
                        if response.status == 200:  # Проверка успешности запроса
                            data = await response.json()
                            rate = data["conversion_rates"].get(target_currency, None)

                            if rate is not None:
                                return rate
                            else:
                                logger.info(f"Валюта {target_currency} не найдена")
                                return None
                except (
                    aiohttp.TimeoutError,
                    aiohttp.ConnectionError,
                ) as e:  # обработка ошибок Timeout и ConnectionError
                    await self.handle_network_error(e, attempt)
                except RequestException as e:
                    raise e
            return None

    async def handle_network_error(
        self,
        error,
        attempt,
    ):

        delay = 2**attempt
        if attempt < self.max_retry - 1:
            logger.info(f"{error}, повтор через {delay}")
            await asyncio.sleep(delay)  # Используем asyncio.sleep для ожидания
        else:
            logger.info("Превышено время ожидания после всех попыток")

    async def convert_price(
        self,
        price: float,
        from_currency: str,
        to_currency: str,
    ) -> Optional[float]:

        if from_currency == to_currency:
            return price
        rate = await self.get_exchange_rate(
            from_currency,
            to_currency,
        )
        if rate is None:
            return None
        return price * rate
