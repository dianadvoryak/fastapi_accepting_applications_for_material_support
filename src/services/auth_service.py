from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.auth_config import security
from src.core.security import hash_password, verify_password
from src.models import User
from src.schema.auth import UserRegisterSchema, UserLoginSchema


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def register(self, data: dict):
        # Проверяем, существует ли пользователь с таким username или email
        query = select(User).where((User.username == data["username"]) | (User.email == data["email"]))
        result = await self.db_session.execute(query)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем или email уже зарегистрирован"
            )

        # Создаем объект нового пользователя, хэшируя пароль
        new_user = User(
            username=data["username"],
            email=data["email"],
            password_hash=hash_password(data["password"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
            department=data["department"]
        )

        self.db_session.add(new_user)
        await self.db_session.commit()
        await self.db_session.refresh(new_user)
        return new_user

    async def login(self, creds: dict):
        # Ищем пользователя в БД по username
        result = await self.db_session.execute(select(User).where(User.username == creds["username"]))
        user = result.scalars().first()

        # Проверяем пароль
        if not user or not verify_password(creds["password"], user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ваш аккаунт заблокирован"
            )

        # Создаем JWT токен, привязывая его к ID пользователя (конвертируем UUID в строку)
        token = security.create_access_token(uid=str(user.id))

        # Возвращаем токен клиенту в формате OAuth2 standard
        return {
            "access_token": token,
            "token_type": "bearer"
        }

