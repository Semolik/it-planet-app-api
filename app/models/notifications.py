from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship
from uuid import uuid4


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    message = Column(String, nullable=False)
    header = Column(String, nullable=False)
    read = Column(Boolean, nullable=False, default=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
