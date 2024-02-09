from datetime import datetime
import uuid
from cruds.base_crud import BaseCRUD
from models.chats import Chat, Message
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class ChatsCrud(BaseCRUD):
    async def get_user_chats(self, user_id: uuid.UUID, page: int, page_size: int = 10):
        end = page * page_size
        start = end - page_size
        query = await self.db.execute(
            select(Chat).join(Message, Chat.id == Message.chat_id)
            .where((Chat.user_id_1 == user_id) | (Chat.user_id_2 == user_id))
            .order_by(Message.creation_date.desc())
            .slice(start, end).options(selectinload(Chat.last_message).selectinload(Message.from_user))
        )
        return query.scalars().all()

    async def read_message(self, message: Message):
        message.read = True
        message.read_date = datetime.now()
        return await self.update(message)

    async def get_message(self, message_id: uuid.UUID):
        query = await self.db.execute(
            select(Message).where(Message.id == message_id).options(
                selectinload(Message.from_user), selectinload(Message.chat))
        )
        return query.scalars().first()

    async def create_chat(self, user_id_1: uuid.UUID, user_id_2: uuid.UUID):
        return await self.create(Chat(user_id_1=user_id_1, user_id_2=user_id_2))

    async def get_chat(self, chat_id: uuid.UUID):
        query = await self.db.execute(
            select(Chat).where(Chat.id == chat_id).options(
                selectinload(Chat.last_message).selectinload(Message.from_user))
        )
        return query.scalars().first()

    async def get_chat_by_users(self, user_id_1: uuid.UUID, user_id_2: uuid.UUID):
        query = await self.db.execute(
            select(Chat).where(
                ((Chat.user_id_1 == user_id_1) & (Chat.user_id_2 == user_id_2)) |
                ((Chat.user_id_1 == user_id_2) & (Chat.user_id_2 == user_id_1))
            )
        )
        return query.scalars().first()

    async def create_message(self, chat_id: uuid.UUID, from_user_id: uuid.UUID, content: str):
        return await self.create(Message(chat_id=chat_id, from_user_id=from_user_id, content=content))

    async def get_messages(self, chat_id: uuid.UUID, page: int, page_size: int = 10):
        end = page * page_size
        start = end - page_size
        query = await self.db.execute(
            select(Message).where(Message.chat_id == chat_id)
            .order_by(Message.creation_date.desc())
            .slice(start, end).options(selectinload(Message.from_user))
        )
        return query.scalars().all()
