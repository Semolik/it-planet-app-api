from fastapi import APIRouter, Depends, HTTPException, Path
from schemas.chats import Message
from notifier import get_notifier
from users_controller import current_active_user
from db.db import get_async_session
from cruds.chats_crud import ChatsCrud
from uuid import UUID


api_router = APIRouter(tags=["messages"], prefix="/messages")


@api_router.post("/{massage_id}/read", status_code=204)
async def read_message(massage_id: UUID = Path(..., description='ID сообщения'), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Отмечает сообщение как прочитанное.'''
    db_message = await ChatsCrud(db).get_message(message_id=massage_id)
    if not db_message or not db_message.can_read(current_user.id):
        raise HTTPException(status_code=404, detail='Сообщение не найдено')
    if db_message.from_user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail='Нельзя отметить как прочитанное свое сообщение')
    if db_message.read:
        raise HTTPException(
            status_code=400, detail='Сообщение уже прочитано')
    chat_notifier = get_notifier(f'chat_{db_message.chat_id}')()
    await chat_notifier.push(
        user_id=db_message.get_to_user_id(from_user_id=current_user.id),
        data=Message.model_validate(db_message).model_dump_json()
    )
    await ChatsCrud(db).read_message(db_message)
