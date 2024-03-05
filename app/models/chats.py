
from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, DateTime, String, func, select
from sqlalchemy.orm import relationship, column_property, object_session
from uuid import uuid4
from sqlalchemy.ext.hybrid import hybrid_property


class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey(
        'chats.id', ondelete="CASCADE"), nullable=False)
    from_user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    content = Column(String, nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    read = Column(Boolean, nullable=False, default=False)
    updated = Column(Boolean, nullable=False, default=False)
    read_date = Column(DateTime(timezone=True))
    chat = relationship("Chat", foreign_keys=[chat_id])
    from_user = relationship("User", foreign_keys=[from_user_id])

    def can_read(self, user_id: UUID):
        return user_id == self.chat.user_id_1 or user_id == self.chat.user_id_2

    def get_to_user_id(self, from_user_id: UUID):
        return self.chat.user_id_1 if from_user_id == self.chat.user_id_2 else self.chat.user_id_2


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id_1 = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete="CASCADE"), nullable=False)
    user_1 = relationship("User", foreign_keys=[user_id_1])
    user_id_2 = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete="CASCADE"), nullable=False)
    user_2 = relationship("User", foreign_keys=[user_id_2])
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    last_message = relationship(
        Message,
        primaryjoin="and_(Message.chat_id == Chat.id, Message.creation_date == select(func.max(Message.creation_date)).where(Message.chat_id == Chat.id).correlate(Chat).scalar_subquery())",
        uselist=False,
        viewonly=True
    )
    messages = relationship(Message, backref="chat",
                            cascade="all, delete-orphan")

    def can_read(self, user_id: UUID):
        return user_id == self.user_id_1 or user_id == self.user_id_2
