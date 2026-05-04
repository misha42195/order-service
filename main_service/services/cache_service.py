import os
import redis.asyncio as redis
import json
from typing import Optional


def parse_redis_url(url: str) -> tuple:
    """Парсит REDIS_URL вида redis://host:6379 в (host, port)"""
    # Убираем redis://
    url = url.replace("redis://", "")
    parts = url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 6379
    return host, port


class CacheService:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
    ):
        # Если REDIS_URL установлен - используем его
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            host, port = parse_redis_url(redis_url)

        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
        )

    async def get_products(
        self,
    ) -> Optional[list]:
        """Получить список товара из кэша"""
        cached_data = await self.redis_client.get("products:all")
        if cached_data:
            return json.loads(cached_data)
        return None

    async def set_products(
        self,
        products: list,
        ttl: int = 3600,
    ):
        """Сохранить список товаров в кэш"""
        await self.redis_client.setex(
            "products:all",
            ttl,
            json.dumps(products),
        )

    async def get_product(
        self,
        product_id: int,
    ) -> Optional[dict]:
        """Получить товар из кеша"""
        cached_data = await self.redis_client.get(
            f"product:{product_id}",
        )
        if cached_data:
            return json.loads(cached_data)
        return None

    async def set_product(
        self,
        product_id: int,
        product: dict,
        ttl: int = 3600,
    ):
        """Сохранить товар в кэш"""
        await self.redis_client.setex(
            f"product:{product_id}",
            ttl,
            json.dumps(product),
        )

    async def invalidate_product(
        self,
        product_id: int,
    ):
        """Инвалидировать товар их кэша"""
        await self.redis_client.delete(
            f"product:{product_id}",
        )
        await self.redis_client.delete(
            "products:all",
        )
