import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.dependencies import get_current_user, allow_executor_or_admin, allow_admin_only
from src.models import User
from src.schema.tickets import TicketCreateSchema, TicketResponseSchema, TicketStatus
from src.services.TicketService import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])

# Фабрика для сервиса
def get_ticket_service(db: AsyncSession = Depends(get_async_session)) -> TicketService:
    return TicketService(db)


# 1. СОЗДАТЬ ЗАЯВКУ: Доступно ВСЕМ авторизованным пользователям
@router.post("/", response_model=TicketResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreateSchema,
    current_user: User = Depends(get_current_user), # Любой вошедший юзер
    ticket_service: TicketService = Depends(get_ticket_service)
):
    # Передаем id создателя прямо из токена
    return await ticket_service.create_new_ticket(ticket_data, creator=current_user)


# 2. ВЗЯТЬ В РАБОТУ / ВЫПОЛНИТЬ: Только Executor (или Admin для гибкости)
@router.post("/{ticket_id}/assign", response_model=TicketResponseSchema)
async def assign_ticket(
    ticket_id: uuid.UUID,
    status: TicketStatus,
    # Наша зависимость гарантирует, что сюда попадут только EXECUTOR или ADMIN
    current_user: User = Depends(allow_executor_or_admin), # Только исполнитель или админ
    ticket_service: TicketService = Depends(get_ticket_service)
):
    # Передаем объект пользователя целиком для проверки его роли внутри сервиса
    return await ticket_service.update_ticket_status(
            current_user=current_user,
            ticket_id=ticket_id,
            new_status=status,
        )


# 3. ЗАКРЫТЬ ЗАЯВКУ (closed_at): Только Админ
@router.post("/{ticket_id}/close", response_model=TicketResponseSchema)
async def close_ticket(
    ticket_id: uuid.UUID,
    current_user: User = Depends(allow_admin_only), # Строго Админ
    ticket_service: TicketService = Depends(get_ticket_service)
):
    return await ticket_service.close_ticket_by_admin(ticket_id)


# 4. УДАЛИТЬ ПОЛНОСТЬЮ: Только Админ
@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: uuid.UUID,
    current_user: User = Depends(allow_admin_only), # Строго Админ
    ticket_service: TicketService = Depends(get_ticket_service)
):
    await ticket_service.hard_delete_ticket(ticket_id)
    return None
