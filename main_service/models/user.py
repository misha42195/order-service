from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    field_validator,
)
from typing import Annotated
from annotated_types import (
    Ge,
    MaxLen,
    MinLen,
)


class UserBase(BaseModel):

    name: Annotated[str, MinLen(3), MaxLen(50)]
    email: Annotated[str, EmailStr]
    balance: Annotated[float, Ge(0)]

    def get_info(self):
        return "Пользователь: " + self.name + ", Email: " + self.email


class UserCreate(UserBase):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Название не может быть пустым")
        return v.strip()


class UserPutUpdate(UserBase):

    class ConfigDict:
        from_attributes = True


class UserPatchUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    balance: float | None = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    pass

    class ConfigDict:
        from_attributes = True


class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def get_info(self):
        return "Пользователь: " + self.name + ", Email: " + self.email
