import logging

import bcrypt
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from passlib.context import CryptContext
from jose import (
    JWTError,
    jwt,
)
from datetime import (
    datetime,
    timedelta,
)


from core.config import settings

"""
1) при вызове функции представления вводим логин и пароль для пользователя
2) по данным полям получаем пользователя из базы данных
3) берем поля пользователя, создаем словарь с его данными (email, name)
вызваем метод для создания токена (create_access_toke) 
 
"""
logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

static_api_token = HTTPBearer(
    scheme_name="Static API token",
    description="Static API token for developer portal",
    auto_error=True,
)


def get_password_hash(password: str) -> str:
    # Превращаем пароль в байты, генерируем соль и хешируем
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Сравниваем чистый пароль с хешем из базы
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.SECRET_KEY,
        algorithm=settings.auth.ALGORITHM,
    )
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(static_api_token),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен отсутствует",
        )

    token = credentials.credentials
    print("TOKEN", token)
    try:
        payload = jwt.decode(
            token,
            settings.auth.SECRET_KEY,
            algorithms=[settings.auth.ALGORITHM],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Нет пользователя",
            )
        print("USER", user_id)
        return int(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
