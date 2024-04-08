from datetime import datetime
import uuid
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from models.locations import Institution


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    register_date = Column(DateTime(timezone=True), server_default=func.now())
    birthdate = Column(DateTime(timezone=True), nullable=False)
    image_id = Column(UUID(as_uuid=True), ForeignKey(
        'images.id', ondelete='SET NULL'), nullable=True)
    image = relationship("Image", foreign_keys=[
                         image_id], cascade="all,delete")
    description = Column(String, nullable=False, default='')
    verified = Column(Boolean, nullable=False, default=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey(
        Institution.id), nullable=True)
    institution = relationship(Institution, foreign_keys=[institution_id])
    hobbies = relationship("Hobby", secondary="user_hobbies")

    @property
    def age(self) -> int | None:
        today = datetime.now().date()
        age = today.year - self.birthdate.year
        if today.month < self.birthdate.month or (today.month == self.birthdate.month and today.day < self.birthdate.day):
            age -= 1
        return age


class UserLike(Base):
    __tablename__ = "user_likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id',ondelete='CASCADE'
        ), nullable=False)
    user = relationship(User, foreign_keys=[user_id])
    liked_user_id = Column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    liked_user = relationship(User, foreign_keys=[liked_user_id])
    like = Column(Boolean, nullable=False, default=True)
    like_date = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
