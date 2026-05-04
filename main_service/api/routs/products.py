from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from database.connection import get_db
from database.models import Product
from dependencies import get_current_user
from models.product import ProductCreate
from services.cache_service import CacheService

router = APIRouter(tags=["products"])
cache_service = CacheService()


@router.get("/products")
async def get_products(
    response: Response,
    page: int = Query(1, ge=1, description="Начальная страница"),
    per_page: int = Query(10, ge=10, le=100, description="Кол-во товаров на странице"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Возврат списка товаров c метаданными"""
    try:
        # получение из кеша
        products_data = await cache_service.get_products()

        # если нет кеша то запрос к базе
        if not products_data:
            result = await db.execute(select(Product))  # список продуктов
            products = result.scalars().all()

            if not products:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Нет товаров",
                )
            # список из словарей в котором содержаться поля продуктов, каждый словарь это отдельный продукт
            products_data = [
                ProductCreate.model_validate(p).model_dump() for p in products
            ]

            # Сохранение в кэш
            await cache_service.set_products(products_data)

            response.headers["Cache-Control"] = "public, max-age=60"

        total_count = len(products_data)
        offset = (page - 1) * per_page
        limit = offset + per_page
        product_page = products_data[offset:limit]

        return {
            "products": product_page,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page,
            },
        }
    except HTTPException as ex:
        raise ex

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка на стороне сервера {e}",
        )


@router.put("/products/{product_id}")
async def full_update_product(
    product_id: int,
    response: Response,
    product_put: ProductCreate,
    _=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )  # список продуктов
        product = result.scalars().first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Продукт с ID {product_id} не найден",
            )
        update_data = product_put.model_dump()  # получаем словарь с полями
        for k, v in update_data.items():
            setattr(product, k, v)  # устанавливаем поля для объекта из базы

        await db.commit()
        await db.refresh(product)
        await cache_service.invalidate_product(
            product_id=product_id,
        )

        # запрещаем кеширование
        response.headers["Cache-Control"] = "no-cache, no-store"

        return {"product": product}
    except HTTPException as ex:
        raise ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка на стороне БД {e}",
        )


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: int,
    response: Response,
    _=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(
            select(Product).where(Product.id == product_id),
        )
        product = result.scalars().first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Продукт с ID {product_id} не найден.",
            )
        await db.delete(product)
        await db.commit()

        await cache_service.invalidate_product(
            product_id=product_id,
        )

        response.headers["Cache-Control"] = "no-cache, no-store"

        return None
    except HTTPException as ex:
        raise ex
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка на стороен БД {e}",
        )


@router.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_in: ProductCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        result = await db.execute(
            select(Product).where(Product.name == product_in.name)
        )
        product = result.scalars().first()
        if product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Продукт с таким именем {product.name} уже существует.",
            )
        new_product = Product(
            **product_in.model_dump(),
        )
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        await cache_service.invalidate_product(
            product_id=new_product.id,
        )
        response.headers["Cache-Control"] = "no-cache, no-store"

        return {
            "name": new_product.name,
            "price": new_product.price,
        }
    except HTTPException as ex:
        raise ex
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка на стороне базы данных {e}.",
        )
