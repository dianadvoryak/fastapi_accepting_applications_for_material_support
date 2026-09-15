import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.models import BaseModel


# Перечисление для ролей пользователей
class UserRole(PyEnum):
    USER = "user"  # Обычный сотрудник (создает заявки)
    EXECUTOR = "executor"  # Исполнитель / Техник (берет заявки в работу)
    ADMIN = "admin"  # Администратор системы


class User(BaseModel):
    __tablename__ = "users"

    # Идентификация
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # Хеш пароля

    # Данные сотрудника (то, что вы просили)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)  # Отдел сотрудника

    # Роли и права
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
    )

    # Статус аккаунта
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Доступ в админку

    # Системные таймстампы
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Связи (Optional: для удобного обращения в коде, например user.created_tickets)
    # back_populates связывает эту модель с моделью Ticket
    created_tickets: Mapped[List["Ticket"]] = relationship(
        "Ticket",
        foreign_keys="[Ticket.creator_id]",
        back_populates="creator"
    )
    assigned_tickets: Mapped[List["Ticket"]] = relationship(
        "Ticket",
        foreign_keys="[Ticket.assignee_id]",
        back_populates="assignee"
    )
