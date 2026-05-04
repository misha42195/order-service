import logging
from datetime import timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import User
from dependencies import (
    verify_password,
    create_access_token,
    get_password_hash,
)
from models.user import UserCreate

router = APIRouter(tags=["login"])
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем, существует ли уже пользователь с таким email
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован",
        )

    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        balance=0.0,
    )

    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)  # Чтобы получить id нового пользователя
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении в базу")

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "message": "Пользователь успешно создан",
    }


@router.post("/login")
async def login_access_token(
    # Указываем правильный тип для асинхронной сессии
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):

    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
        },
        expires_delta=timedelta(minutes=30),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
    }
