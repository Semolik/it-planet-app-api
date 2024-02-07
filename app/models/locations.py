from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from uuid import uuid4


class City(Base):
    __tablename__ = 'cities'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)


class Institution(Base):
    __tablename__ = 'institutions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    city_id = Column(UUID(as_uuid=True), ForeignKey(City.id), nullable=False)
    city = relationship(City, foreign_keys=[city_id])
