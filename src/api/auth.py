from fastapi import APIRouter, HTTPException, Response, Depends
from authx import AuthX, AuthXConfig

from src.core.auth_config import security
from src.core.config import settings
from pydantic import BaseModel


import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from authx import AuthX, AuthXConfig
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr

from src.core.config import settings
from src.core.db import get_async_session
from src.core.dependencies import get_current_user
from src.core.security import hash_password, verify_password  # Ваши функции хэширования
from src.models import User  # Наша модель из прошлых шагов
from src.schema.auth import UserResponseSchema, UserRegisterSchema, UserLoginSchema
from src.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegisterSchema, db: AsyncSession = Depends(get_async_session)):
    auth_service = AuthService(db)
    new_user = await auth_service.register(data.model_dump())
    return new_user


@router.post("/login")
async def login(creds: UserLoginSchema, db: AsyncSession = Depends(get_async_session)):
    auth_service = AuthService(db)
    access_token = await auth_service.login(creds.model_dump())
    return access_token


@router.get("/me", response_model=UserResponseSchema)
async def get_me(current_user: User = Depends(get_current_user)):
    """Эндпоинт возвращает профиль текущего авторизованного пользователя"""
    return current_user