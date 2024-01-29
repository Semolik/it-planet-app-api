from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, DateTime, func
from uuid import uuid4


class VerificationRequest(Base):
    __tablename__ = 'verification_requests'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed = Column(Boolean, nullable=False, default=False)
