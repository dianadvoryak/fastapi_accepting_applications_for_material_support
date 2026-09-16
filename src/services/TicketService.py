from datetime import datetime
import uuid
from fastapi import HTTPException, status

from src.models import User
from src.models.tickets import Ticket
from src.models.users import UserRole
from src.schema.tickets import TicketCreateSchema, TicketStatus


class TicketService:
    def __init__(self, db):
        self.db = db

    async def create_new_ticket(self, data: TicketCreateSchema, creator: User):
        # data.model_dump() теперь содержит только title, description и priority
        ticket = Ticket(
            **data.model_dump(),
            creator_id=creator.id,
            department=creator.department,  # Отдел подтягивается автоматически из профиля создателя!
            status=TicketStatus.NEW
        )

        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)  # Рекомендуется добавить для обновления ID и дат в объекте
        return ticket

    async def update_ticket_status(self, current_user: User, ticket_id: uuid.UUID, new_status: TicketStatus = TicketStatus.NEW):
        # 1. Достаем заявку из базы данных
        ticket = await self.db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заявка не найдена"
            )

        # Здесь можно добавить проверку: например, обычный EXECUTOR не может перевести в DONE без проверки
        if new_status == TicketStatus.DONE and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Only admin can close tickets")

        # 2. Проверяем, не закрыта ли уже заявка
        if ticket.status in [TicketStatus.CLOSED, TicketStatus.RESOLVED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя взять в работу уже закрытую или решенную заявку"
            )

        # 3. ГЛАВНАЯ ПРОВЕРКА: Если заявка ОЧЕНЬ занята кем-то другим
        if ticket.assignee_id is not None and ticket.assignee_id != current_user.id:
            # Если это не админ — запрещаем действие
            if current_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Эта заявка уже взята в работу другим исполнителем. Переназначить может только администратор."
                )
            # Если это админ — логика пойдет дальше и перезапишет исполнителя

        # 4. Обновляем статус и назначаем пользователя
        ticket.assignee_id = current_user.id
        ticket.status = new_status

        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket


    async def close_ticket_by_admin(self, ticket_id: uuid.UUID):
        ticket = await self.db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = datetime.utcnow()  # Проставляем дату закрытия
        await self.db.commit()
        return ticket

    async def hard_delete_ticket(self, ticket_id: uuid.UUID):
        ticket = await self.db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        await self.db.delete(ticket)
        await self.db.commit()
