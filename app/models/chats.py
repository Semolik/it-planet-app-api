
from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, DateTime, String, func
from sqlalchemy.orm import relationship
from uuid import uuid4


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id_1 = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    user_id_2 = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    last_message = relationship(
        "Message",
        primaryjoin="Message.chat_id == Chat.id",
        uselist=False,
        viewonly=True,
        order_by="desc(Message.creation_date)"
    )


class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey(
        'chats.id'), nullable=False)
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
