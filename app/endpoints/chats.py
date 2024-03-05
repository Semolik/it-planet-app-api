from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, WebSocket, WebSocketDisconnect, WebSocketException
from utilities.chats import set_chat_info
from utilities.websockets import get_user_from_cookie
from users_controller import current_active_user
from db.db import get_async_session
from cruds.chats_crud import ChatsCrud
from uuid import UUID
from schemas.chats import Chat, ChatWithUsers, Message
from notifier import Notifier, get_notifier

api_router = APIRouter(tags=["chats"], prefix="/chats")


@api_router.get("", response_model=List[ChatWithUsers])
async def get_chats(
    query: str = Query(None, description='Поиск по имени пользователя'),
    page: int = Query(ge=1),
    db=Depends(get_async_session),
    current_user=Depends(current_active_user)
):
    '''Возвращает список чатов пользователя.'''
    chats = await ChatsCrud(db).get_user_chats(user_id=current_user.id, page=page, search_query=query)
    return [set_chat_info(chat=chat, unread_count=unread_count) for chat, unread_count in chats]


@api_router.post("", response_model=Chat)
async def create_chat(message: str, user_id: UUID = Query(..., description='ID пользователя, с которым создается чат'), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Создает чат с пользователем.'''
    db_chat = await ChatsCrud(db).get_chat_by_users(user_id_1=current_user.id, user_id_2=user_id)
    if db_chat:
        raise HTTPException(status_code=400, detail='Чат уже существует')
    db_chat = await ChatsCrud(db).create_chat(from_user_id=current_user.id, to_user_id=user_id, message=message)
    return await ChatsCrud(db).get_chat(chat_id=db_chat.id)


@api_router.delete("/{chat_id}", status_code=204)
async def delete_chat(chat_id: UUID = Path(..., description='ID чата'), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Удаляет чат.'''
    db_chat = await ChatsCrud(db).get_chat(chat_id=chat_id)
    if not db_chat:
        raise HTTPException(status_code=404, detail='Чат не найден')
    if not db_chat.can_read(user_id=current_user.id):
        raise HTTPException(
            status_code=403, detail='У вас нет доступа к этому чату')
    await ChatsCrud(db).delete(db_chat)


@api_router.get("/{chat_id}", response_model=ChatWithUsers)
async def get_chat(chat_id: UUID = Path(..., description='ID чата'), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Возвращает чат по его ID.'''
    db_chat = await ChatsCrud(db).get_chat(chat_id=chat_id)
    if not db_chat:
        raise HTTPException(status_code=404, detail='Чат не найден')
    if not db_chat.can_read(user_id=current_user.id):
        raise HTTPException(
            status_code=403, detail='У вас нет доступа к этому чату')
    db_chat.current_user_id = current_user.id
    unreaded = await ChatsCrud(db).get_unread_count(user_id=current_user.id, chat_id=chat_id)
    return set_chat_info(chat=db_chat, unread_count=unreaded)


@api_router.post("/{chat_id}/messages", response_model=Message)
async def send_message(content: str, chat_id: UUID = Path(..., description='ID чата'), db=Depends(get_async_session), current_user=Depends(current_active_user), notifier: Notifier = Depends(get_notifier('chats'))):
    '''Отправляет сообщение в чат.'''
    db_chat = await ChatsCrud(db).get_chat(chat_id=chat_id)
    if not db_chat:
        raise HTTPException(status_code=404, detail='Чат не найден')
    if not db_chat.can_read(user_id=current_user.id):
        raise HTTPException(
            status_code=403, detail='У вас нет доступа к этому чату')
    db_message = await ChatsCrud(db).create_message(chat_id=chat_id, from_user_id=current_user.id, content=content)
    db_message = await ChatsCrud(db).get_message(message_id=db_message.id)
    db_chat.last_message = db_message
    db_chat.current_user_id = current_user.id
    to_user_id = db_message.get_to_user_id(from_user_id=current_user.id)
    unreaded = await ChatsCrud(db).get_unread_count(user_id=to_user_id, chat_id=chat_id)
    await notifier.push(
        user_id=to_user_id,
        data=set_chat_info(
            chat=db_chat, unread_count=unreaded).model_dump_json()
    )
    chat_notifier = get_notifier(f'chat_{chat_id}')()
    await chat_notifier.push(
        user_id=to_user_id,
        data=Message.model_validate(db_message).model_dump_json()
    )
    return db_message


@api_router.get("/{chat_id}/messages", response_model=List[Message])
async def get_messages(chat_id: UUID = Path(..., description='ID чата'), page: int = Query(ge=1), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Возвращает список сообщений в чате.'''
    db_chat = await ChatsCrud(db).get_chat(chat_id=chat_id)
    if not db_chat:
        raise HTTPException(status_code=404, detail='Чат не найден')
    if not db_chat.can_read(user_id=current_user.id):
        raise HTTPException(
            status_code=403, detail='У вас нет доступа к этому чату')
    return await ChatsCrud(db).get_messages(chat_id=chat_id, page=page)


@api_router.websocket("/{chat_id}/messages/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: UUID = Path(..., description='ID чата'),
    current_user=Depends(get_user_from_cookie),
    db=Depends(get_async_session)
):
    if not current_user:
        raise WebSocketException(code=403, reason="Access denied")
    chat = await ChatsCrud(db).get_chat(chat_id=chat_id)
    if not chat:
        raise WebSocketException(code=404, reason="Chat not found")
    if not chat.can_read(user_id=current_user.id):
        raise WebSocketException(code=403, reason="Access denied")
    notifier: Notifier = get_notifier(f'chat_{chat_id}')()
    try:
        await notifier.connect(user_id=current_user.id, websocket=websocket)
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        notifier.remove(user_id=current_user.id, websocket=websocket)


@api_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user=Depends(get_user_from_cookie), notifier: Notifier = Depends(get_notifier('chats'))):
    if not current_user:
        raise WebSocketException(code=403, reason="Access denied")
    try:
        await notifier.connect(user_id=current_user.id, websocket=websocket)
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        notifier.remove(user_id=current_user.id, websocket=websocket)
