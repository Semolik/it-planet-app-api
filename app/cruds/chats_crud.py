from datetime import datetime
from typing import List, Tuple
import uuid
from models.user import User
from cruds.base_crud import BaseCRUD
from models.chats import Chat, Message
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func, or_, update
from cruds.users_cruds import UsersCrud


class ChatsCrud(BaseCRUD):

    def get_unread_messages_subquery(self, user_id: uuid.UUID):
        unread_messages_subquery = select(
            func.count(Message.id).label('unread_count')
        ).join(Message.chat).filter(
            Message.chat_id == Chat.id,
            Message.from_user_id != user_id,
            Message.read == False
        ).scalar_subquery()
        return unread_messages_subquery

    async def read_messages(self, chat_id: uuid.UUID, user_id: uuid.UUID):
        await self.db.execute(
            update(Message).where(
                Message.chat_id == chat_id,
                Message.from_user_id != user_id,
                Message.read == False
            ).values(
                read=True,
                read_date=datetime.now()
            )
        )
        await self.db.commit()

    async def get_user_chats(self, user_id: uuid.UUID, page: int, page_size: int = 20, search_query: str = None) -> List[Tuple[Chat, int]]:
        '''Returns user chats with unread messages count'''
        end = page * page_size
        start = end - page_size
        subquery = select(
            Message.chat_id,
            func.max(Message.creation_date).label('max_creation_date')
        ).group_by(Message.chat_id).subquery()

        query = select(Chat, self.get_unread_messages_subquery(user_id=user_id))\
            .join(subquery, and_(Chat.id == subquery.c.chat_id))\
            .join(Message, and_(Message.chat_id == Chat.id, Message.creation_date == subquery.c.max_creation_date))\
            .where((Chat.user_id_1 == user_id) | (Chat.user_id_2 == user_id))

        if search_query:
            query = query.join(
                User, or_(Chat.user_id_1 == User.id, Chat.user_id_2 == User.id)
            ).where(User.name.like(f'%{search_query}%'))
            if user_id:
                query = query.where(User.id != user_id)

        result = await self.db.execute(
            query
            .where(User.name.like(f'%{search_query}%') & (User.id != user_id) if search_query else True)
            .order_by(subquery.c.max_creation_date.desc())
            .slice(start, end)
            .options(
                *self.selectinload_chat()
            )
        )
        return result.all()

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

    async def create_chat(self, from_user_id: uuid.UUID, to_user_id: uuid.UUID, message: str):
        chat = await self.create(Chat(user_id_1=from_user_id, user_id_2=to_user_id))
        await self.create(Message(chat_id=chat.id, from_user_id=from_user_id, content=message))
        return chat

    async def get_chat(self, chat_id: uuid.UUID):
        query = await self.db.execute(
            select(Chat).where(Chat.id == chat_id).options(
                *self.selectinload_chat()
            )
        )
        return query.scalars().first()

    async def get_chat_by_users(self, user_id_1: uuid.UUID, user_id_2: uuid.UUID):
        query = await self.db.execute(
            select(Chat).where(
                ((Chat.user_id_1 == user_id_1) & (Chat.user_id_2 == user_id_2)) |
                ((Chat.user_id_1 == user_id_2) & (Chat.user_id_2 == user_id_1))
            )
            .options(
                *self.selectinload_chat()
            )
        )
        return query.scalars().first()

    def selectinload_chat(self):
        return [
            selectinload(Chat.last_message)
            .selectinload(Message.from_user)
            .options(
                *UsersCrud.selectinload_user_options()
            ),
            selectinload(Chat.user_1)
            .options(
                *UsersCrud.selectinload_user_options()
            ),
            selectinload(Chat.user_2)
            .options(
                *UsersCrud.selectinload_user_options()
            ),
        ]

    async def get_unread_count(self, chat_id: uuid.UUID, user_id: uuid.UUID):
        query = await self.db.execute(
            select(func.count(Message.id)).join(Message.chat).filter(
                Message.chat_id == chat_id,
                Message.from_user_id != user_id,
                Message.read == False
            )
        )
        return query.scalar()

    async def create_message(self, chat_id: uuid.UUID, from_user_id: uuid.UUID, content: str) -> Message:
        return await self.create(Message(chat_id=chat_id, from_user_id=from_user_id, content=content))

    async def get_messages(self, chat_id: uuid.UUID, page: int, page_size: int = 20):
        end = page * page_size
        start = end - page_size
        query = await self.db.execute(
            select(Message).where(Message.chat_id == chat_id)
            .order_by(Message.creation_date.desc())
            .slice(start, end).options(selectinload(Message.from_user).options(
                *UsersCrud.selectinload_user_options()
            ))

        )
        return query.scalars().all()
