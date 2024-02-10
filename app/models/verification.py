from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, DateTime, String, func
from uuid import uuid4
from sqlalchemy.orm import relationship


class VerificationRequest(Base):
    __tablename__ = 'verification_requests'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    updated_date = Column(DateTime(timezone=True),
                          onupdate=func.now())
    reviewed = Column(Boolean, nullable=False, default=False)
    name = Column(String, nullable=False)
    birthdate = Column(DateTime, nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey(
        'institutions.id'), nullable=False)
    institution = relationship("Institution", foreign_keys=[institution_id])
    real_photo_id = Column(UUID(as_uuid=True), ForeignKey(
        'images.id'), nullable=False)
    real_photo = relationship("Image", foreign_keys=[
                              real_photo_id], cascade="all,delete")
    id_photo_id = Column(UUID(as_uuid=True), ForeignKey(
        'images.id'), nullable=False)
    id_photo = relationship("Image", foreign_keys=[
                            id_photo_id], cascade="all,delete")
