from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, DateTime, func, String
from uuid import uuid4


class UserHobby(Base):
    __tablename__ = 'user_hobbies'
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), primary_key=True)
    hobby_id = Column(UUID(as_uuid=True), ForeignKey(
        'hobbies.id'), primary_key=True)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())


class Hobby(Base):
    __tablename__ = 'hobbies'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
