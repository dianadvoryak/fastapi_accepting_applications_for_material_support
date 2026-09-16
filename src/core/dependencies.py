import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.auth_config import security
from src.core.db import get_async_session
from src.models.users import User, UserRole


# Зависимость (Dependency) для получения текущего пользователя по токену в хедере
async def get_current_user(
        token_payload=Depends(security.access_token_required),
        db: AsyncSession = Depends(get_async_session)
) -> User:
    # AuthX автоматически валидирует токен. Мы достаем uid (sub), сохраненный при логине
    user_id = token_payload.sub

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalars().first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или деактивирован"
        )
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав для выполнения этого действия"
            )
        return current_user

# Удобные алиасы для роутеров
allow_executor_or_admin = RoleChecker([UserRole.EXECUTOR, UserRole.ADMIN])
allow_admin_only = RoleChecker([UserRole.ADMIN])

