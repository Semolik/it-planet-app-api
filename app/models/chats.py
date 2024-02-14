
from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, DateTime, String, func, select
from sqlalchemy.orm import relationship, column_property
from uuid import uuid4
from sqlalchemy.ext.hybrid import hybrid_property


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

    def get_to_user_id(self, from_user_id: UUID):
        return self.chat.user_id_1 if from_user_id == self.chat.user_id_2 else self.chat.user_id_2


class Chat(Base):

    def __init__(self, current_user_id: UUID = None, **kwargs):
        self.current_user_id = current_user_id
        super().__init__(**kwargs)
    __tablename__ = 'chats'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id_1 = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    user_1 = relationship("User", foreign_keys=[user_id_1])
    user_id_2 = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    user_2 = relationship("User", foreign_keys=[user_id_2])
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    last_message = relationship(
        "Message",
        primaryjoin="and_(Message.chat_id == Chat.id, Message.creation_date == select(func.max(Message.creation_date)).where(Message.chat_id == Chat.id).correlate(Chat).scalar_subquery())",
        uselist=False,
        viewonly=True
    )
    current_user_id = None
    # unreaded = column_property(
    #     select(func.count(Message.id))
    #     .where(Message.chat_id == id)
    #     .where(Message.from_user_id != current_user_id)
    #     .where(Message.read == False)
    #     .group_by(Message.chat_id)
    #     .correlate_except(Message)
    #     .as_scalar()
    # )

    # @hybrid_property
    # def unreaded(self):
    #     return self._unreaded

    # @unreaded.expression
    # def unreaded(cls):
    #     if hasattr(cls, '_unreaded'):
    #         return cls._unreaded
    #     cls._unreaded = select(func.count(Message.id)).where(Message.chat_id == cls.id).where(Message.from_user_id != cls.current_user_id).where(
    #         Message.read == False).group_by(Message.chat_id).correlate_except(Message).as_scalar()
    #     return cls._unreaded
