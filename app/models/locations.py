from db.db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from uuid import uuid4


class City(Base):
    __tablename__ = 'cities'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)


class University(Base):
    __tablename__ = 'universities'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    short_name = Column(String, nullable=False)
    institutes = relationship(
        "Institute", back_populates="university", cascade="all, delete-orphan")


class Institute(Base):
    __tablename__ = 'institutes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    university_id = Column(UUID(as_uuid=True), ForeignKey(
        University.id), nullable=True)
    city_id = Column(UUID(as_uuid=True), ForeignKey(City.id), nullable=False)
    university = relationship(University, foreign_keys=[university_id])
    city = relationship(City, foreign_keys=[city_id])
