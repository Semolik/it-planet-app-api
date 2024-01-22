from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import object_session

from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Enum, String, DateTime, func
from sqlalchemy.orm import relationship


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    register_date = Column(DateTime(timezone=True), server_default=func.now())
    birthdate = Column(DateTime(timezone=True), nullable=True)
