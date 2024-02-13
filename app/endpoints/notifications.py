from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, Path
from users_controller import current_active_user
from db.db import get_async_session
from cruds.notifications_crud import NotificationsCrud
from schemas.notifications import Notification

api_router = APIRouter(prefix="/notifications", tags=["notifications"])


@api_router.get("", response_model=List[Notification])
async def get_notifications(db=Depends(get_async_session), current_user=Depends(current_active_user)):
    return await NotificationsCrud(db).get_notifications(current_user.id)


@api_router.get("/unread", response_model=List[Notification])
async def get_unread_notifications(db=Depends(get_async_session), current_user=Depends(current_active_user)):
    return await NotificationsCrud(db).get_notifications(current_user.id, is_read=False)


@api_router.get("/unread/count", response_model=int)
async def get_unread_notifications_count(db=Depends(get_async_session), current_user=Depends(current_active_user)):
    return await NotificationsCrud(db).get_notifications_count(current_user.id, is_read=False)


@api_router.post('/{notification_id}/read', status_code=204)
async def read_notification(notification_id: uuid.UUID = Path(..., description='ID уведомления'),
                            db=Depends(get_async_session), current_user=Depends(current_active_user)):
    notification = await NotificationsCrud(db).get_notification(notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(404, "Уведомление не найдено")
    await NotificationsCrud(db).read_notification(notification)


@api_router.get('/{notification_id}', response_model=Notification)
async def get_notification(notification_id: uuid.UUID = Path(..., description='ID уведомления'), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    notification = await NotificationsCrud(db).get_notification(notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(404, "Уведомление не найдено")
    return notification


@api_router.delete('/{notification_id}', status_code=204)
async def delete_notification(notification_id: uuid.UUID = Path(..., description='ID уведомления'), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    notification = await NotificationsCrud(db).get_notification(notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(404, "Уведомление не найдено")
    await NotificationsCrud(db).delete(notification)
