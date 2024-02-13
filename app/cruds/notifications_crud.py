import uuid
from models.notifications import Notification
from cruds.base_crud import BaseCRUD
from models.locations import Institution
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, select


class NotificationsCrud(BaseCRUD):

    async def get_notification(self, notification_id: uuid.UUID) -> Notification:
        query = await self.db.execute(select(Notification).where(Notification.id == notification_id))
        return query.scalars().first()

    async def read_notification(self, notification: Notification) -> Notification:
        notification.read = True
        return await self.update(notification)

    async def create_notification(self, user_id: uuid.UUID, message: str, header: str) -> Notification:
        return await self.create(
            Notification(
                user_id=user_id,
                message=message,
                header=header
            )
        )

    async def get_notifications(self, user_id: uuid.UUID, is_read: bool = None) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            query = query.where(Notification.read == is_read)
        result = await self.db.execute(query.order_by(Notification.creation_date.desc()))
        return result.scalars().all()

    async def get_notifications_count(self, user_id: uuid.UUID, is_read: bool = None) -> int:
        query = select(func.count()).where(Notification.user_id == user_id)
        if is_read is not None:
            query = query.where(Notification.read == is_read)
        result = await self.db.execute(query)
        return result.scalar()
