from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import object_session

from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Enum, String, DateTime, func, event
from sqlalchemy.orm import relationship
from uuid import uuid4


class Image(Base):
    __tablename__ = 'images'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
