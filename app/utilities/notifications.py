import uuid
from notifier import get_notifier
from sqlalchemy.ext.asyncio import AsyncSession
from cruds.notifications_crud import NotificationsCrud
from schemas.notifications import Notification as NotificationSchema


async def send_notification(user_id: uuid.UUID, message: str, header: str, db: AsyncSession):
    notifier = get_notifier('notifications')()
    db_notification = await NotificationsCrud(db).create_notification(user_id=user_id, message=message, header=header)
    await notifier.push(user_id=user_id, data=NotificationSchema(**db_notification.__dict__).model_dump_json())
    return db_notification
