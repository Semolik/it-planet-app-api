from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, WebSocket, WebSocketDisconnect
from cruds.users_cruds import UsersCrud
from utilities.websockets import get_user_from_cookie
from users_controller import current_active_user, optional_current_user
from db.db import get_async_session
from cruds.chats_crud import ChatsCrud
from uuid import UUID
from schemas.chats import Chat, ChatWithUsers, Message
from notifier import Notifier, get_notifier

notifier = Notifier()

api_router = APIRouter(tags=["chats"], prefix="/chats")


@api_router.get("", response_model=List[ChatWithUsers])
async def get_chats(page: int = Query(ge=1), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Возвращает список чатов пользователя.'''
    return await ChatsCrud(db).get_user_chats(user_id=current_user.id, page=page)


@api_router.post("", response_model=Chat)
async def create_chat(message: str, user_id: UUID = Query(..., description='ID пользователя, с которым создается чат'), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Создает чат с пользователем.'''
    db_chat = await ChatsCrud(db).get_chat_by_users(user_id_1=current_user.id, user_id_2=user_id)
    if db_chat:
        raise HTTPException(status_code=400, detail='Чат уже существует')
    db_chat = await ChatsCrud(db).create_chat(from_user_id=current_user.id, to_user_id=user_id, message=message)
    return await ChatsCrud(db).get_chat(chat_id=db_chat.id)


@api_router.get("/{chat_id}", response_model=ChatWithUsers)
async def get_chat(chat_id: UUID = Path(..., description='ID чата'), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Возвращает чат по его ID.'''
    db_chat = await ChatsCrud(db).get_chat(chat_id=chat_id)
    if not db_chat:
        raise HTTPException(status_code=404, detail='Чат не найден')
    return db_chat


@api_router.post("/{chat_id}/messages", response_model=Message)
async def send_message(content: str, chat_id: UUID = Path(..., description='ID чата'), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Отправляет сообщение в чат.'''
    db_chat = await ChatsCrud(db).get_chat(chat_id=chat_id)
    if not db_chat:
        raise HTTPException(status_code=404, detail='Чат не найден')
    if db_chat.user_id_1 != current_user.id and db_chat.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=403, detail='У вас нет доступа к этому чату')
    db_message = await ChatsCrud(db).create_message(chat_id=chat_id, from_user_id=current_user.id, content=content)
    message_obj = Message(**db_message.__dict__, from_user=current_user)
    await notifier.push(user_id=db_message.get_to_user_id(from_user_id=current_user.id), data=message_obj.model_dump_json())
    return message_obj


@api_router.get("/{chat_id}/messages", response_model=List[Message])
async def get_messages(chat_id: UUID = Path(..., description='ID чата'), page: int = Query(ge=1), db=Depends(get_async_session), current_user=Depends(current_active_user)):
    '''Возвращает список сообщений в чате.'''
    db_chat = await ChatsCrud(db).get_chat(chat_id=chat_id)
    if not db_chat:
        raise HTTPException(status_code=404, detail='Чат не найден')
    if db_chat.user_id_1 != current_user.id and db_chat.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=403, detail='У вас нет доступа к этому чату')
    return await ChatsCrud(db).get_messages(chat_id=chat_id, page=page)


@api_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user=Depends(get_user_from_cookie), notifier: Notifier = Depends(get_notifier('chats'))):
    try:
        await notifier.connect(user_id=current_user.id, websocket=websocket)
        while True:
            data = await websocket.receive_json()
            await websocket.send_json(data=data)
    except WebSocketDisconnect:
        notifier.remove(user_id=current_user.id, websocket=websocket)


@api_router.post("/push")
async def push_to_connected_websockets(data: dict,  current_user=Depends(current_active_user), notifier: Notifier = Depends(get_notifier('chats'))):
    await notifier.push(current_user.id, data=data)
