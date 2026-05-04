from typing import Annotated, List
from annotated_types import (
    MinLen,
    MaxLen,
)
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
)

from models.exeptions import InvalidOrderError


class BaseOrder(BaseModel):
    total: Annotated[float, Field(ge=0)]
    status: Annotated[
        str,
        MinLen(3),
        MaxLen(20),
    ]
    user_id: int
    items: List = []
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseOrder):
    pass


class OrderPutUpdate(BaseOrder):
    pass

    class ConfigDict:
        from_attributes = True


class OrderPatchUpdate(BaseOrder):
    name: str | None = None
    price: float | None = None
    stock: int | None = None

    class ConfigDict:
        from_attributes = True


class OrderResponse(BaseModel):
    price: float

    @field_validator("price")
    def check_price(cls, value):
        if value < 0:
            raise ValueError("Стоимость не может быть отрицательной")
        return value

    class ConfigDict:
        from_attributes = True


class Order:
    def __init__(self, user, products, order_id=None):
        if not products or len(products) == 0:
            raise InvalidOrderError("Заказ невалиден: пустой список товаров")
        self.user = user
        self.products = products
        self.order_id = order_id
        self.total = self.calculate_total()

    def calculate_total(self):
        total = 0
        for product in self.products:
            total = total + product.get_total_price()
        return total

    def __str__(self):
        if self.order_id:
            user_name = self.user.name if hasattr(self.user, "name") else str(self.user)
            return (
                "Заказ #"
                + str(self.order_id)
                + " на сумму "
                + str(self.total)
                + " руб. (Пользователь: "
                + user_name
                + ")"
            )
        else:
            user_name = self.user.name if hasattr(self.user, "name") else str(self.user)
            return (
                "Заказ на сумму "
                + str(self.total)
                + " руб. (Пользователь: "
                + user_name
                + ")"
            )
