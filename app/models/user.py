from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from models.locations import Institute


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    register_date = Column(DateTime(timezone=True), server_default=func.now())
    birthdate = Column(DateTime(timezone=True), nullable=True)
    image_id = Column(UUID(as_uuid=True), ForeignKey(
        'images.id'), nullable=True)
    image = relationship("Image", foreign_keys=[image_id])
    discription = Column(String, nullable=False, default='')
    verified = Column(Boolean, nullable=False, default=False)
    institute_id = Column(UUID(as_uuid=True), ForeignKey(
        Institute.id), nullable=True)
    institute = relationship(Institute, foreign_keys=[institute_id])
