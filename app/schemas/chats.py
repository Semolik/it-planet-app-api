from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from schemas.users import UserReadShort


class Message(BaseModel):
    id: UUID
    chat_id: UUID
    from_user: UserReadShort
    content: str
    creation_date: datetime
    read: bool
    updated: bool


class Chat(BaseModel):
    id: UUID
    user_id_1: UUID
    user_id_2: UUID
    creation_date: datetime
    last_message: Message


class ChatWithUsers(Chat):
    user_1: UserReadShort
    user_2: UserReadShort
