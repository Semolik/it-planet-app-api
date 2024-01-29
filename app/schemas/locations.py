import uuid
from pydantic import BaseModel


class CreateCity(BaseModel):
    name: str


class City(CreateCity):
    id: uuid.UUID


class CreateUniversity(BaseModel):
    name: str


class University(CreateUniversity):
    id: uuid.UUID


class CreateInstitute(BaseModel):
    name: str
    university_id: uuid.UUID
