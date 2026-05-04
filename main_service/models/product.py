from typing import Annotated
from annotated_types import (
    MaxLen,
    MinLen,
    Ge,
)


from pydantic import BaseModel, field_validator, ConfigDict

from models.exeptions import InsufficientStockError, NegativePriceError


class ProductBase(BaseModel):
    """
    Документация для класса
    ProductBase
    :

    id: Идентификатор продукта. Тип данных: целое число.
    name: Название продукта. Тип данных: строка, максимальная длина - 100 символов.
    price: Цена товара. Тип данных: число с плавающей точкой, должна быть больше или равна 1.
    stock: Количество товара в наличии. Тип данных: целое число, должно быть неотрицательным.
    """

    name: Annotated[
        str,
        MinLen(3),
        MaxLen(100),
    ]
    price: Annotated[
        float,
        Ge(1),
    ]
    stock: Annotated[int, Ge(0)]

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(ProductBase):
    pass

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Название не может быть пустым")
        return v.strip()


class ProductPutUpdate(ProductBase):

    class ConfigDict:
        from_attributes = True


class ProductPatchUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    stock: int | None = None

    class ConfigDict:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    @field_validator("price")
    def check_price(cls, value):
        if value < 0:
            raise ValueError("Стоимость не может быть отрицательной")
        return value

    class ConfigDict:
        from_attributes = True


class Product:
    def __init__(self, name, price, quantity):
        if price < 0:
            raise NegativePriceError("Цена не может быть отрицательной")
        self.name = name
        self.price = price
        self.quantity = quantity

    def get_total_price(self) -> float:
        return self.price * self.quantity

    def __str__(self):
        return (
            "Товар: "
            + self.name
            + ", Цена: "
            + str(self.price)
            + " руб., Количество: "
            + str(self.quantity)
        )

    def __repr__(self):
        return (
            "Product('"
            + self.name
            + "', "
            + str(self.price)
            + ", "
            + str(self.quantity)
            + ")"
        )

    def __lt__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price

    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        return self.name == other.name and self.price == other.price

    def sell(self, amount):
        if self.quantity < amount:
            raise InsufficientStockError(
                f"Товара недостаточно. На складе: {self.quantity}, требуется: {amount}"
            )
        self.quantity = self.quantity - amount
