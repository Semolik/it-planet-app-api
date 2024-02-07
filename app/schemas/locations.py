import uuid
from pydantic import BaseModel


class CreateCity(BaseModel):
    name: str


class City(CreateCity):
    id: uuid.UUID


class BaseInstitution(BaseModel):
    name: str


class CreateInstitution(BaseInstitution):
    city_id: uuid.UUID


class Institution(BaseInstitution):
    id: uuid.UUID
    city: City
