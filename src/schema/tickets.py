import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from pydantic import BaseModel, Field

# Перечисления для статусов и приоритетов
class TicketStatus(PyEnum):
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"

    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"

class TicketPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"



class TicketBaseSchema(BaseModel):
    """Базовая схема с общими полями для валидации текста"""
    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Краткий заголовок проблемы",
        examples=["Не работает принтер в бухгалтерии"]
    )
    description: str = Field(
        ...,
        min_length=10,
        description="Полное описание проблемы или заявки",
        examples=["Принтер HP LaserJet не реагирует на отправку документов на печать, горит красная лампочка."]
    )


class TicketCreateSchema(TicketBaseSchema):
    """Схема для создания заявки (Входные данные от пользователя).
    Поля id, creator_id, статус и даты здесь НЕ нужны, они проставляются бэкендом.
    Пользователь присылает ТОЛЬКО заголовок, описание и приоритет.
        """
    priority: TicketPriority = Field(
        default=TicketPriority.MEDIUM,
        description="Приоритет заявки (low, medium, high, critical)"
    )


class TicketResponseSchema(TicketBaseSchema):
    """Схема для ответа клиенту (Выходные данные).
    Сюда включаются все системные поля, которые мы отдаем фронтенду.
    """
    id: uuid.UUID
    status: TicketStatus
    priority: TicketPriority

    department: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Отдел, к которому относится заявка",
        examples=["IT", "Бухгалтерия", "HR"]
    )

    creator_id: uuid.UUID
    assignee_id: Optional[uuid.UUID] = None  # Может быть null, если никто не взял в работу

    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None  # Будет null, пока заявка открыта

    class Config:
        # В Pydantic v2 это свойство позволяет схеме автоматически читать данные
        # прямо из SQLAlchemy моделей (раньше в v1 это был orm_mode = True)
        from_attributes = True

