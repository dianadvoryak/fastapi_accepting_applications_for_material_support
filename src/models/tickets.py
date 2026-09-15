import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.models import BaseModel


# Перечисления для статусов и приоритетов
class TicketStatus(PyEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Ticket(BaseModel):
    __tablename__ = "tickets"

    # Основные поля (Идентификация)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)  # Заголовок
    description: Mapped[str] = mapped_column(Text, nullable=False)   # Описание заявки
    department: Mapped[str] = mapped_column(String(100), nullable=False) # Отдел

    # Пользователи (Внешние ключи)
    # Предполагается, что таблица пользователей называется "users"
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Жизненный цикл и Логика (Что мы добавили)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus), default=TicketStatus.NEW, nullable=False
    )
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False
    )

    # Таймстампы (Временные метки)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Добавить внутрь класса Ticket для связи с User:
    creator: Mapped["User"] = relationship(
        "User", foreign_keys=[creator_id], back_populates="created_tickets"
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assignee_id], back_populates="assigned_tickets"
    )

