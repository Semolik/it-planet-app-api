import uuid
from pydantic import BaseModel


class CreateCity(BaseModel):
    name: str


class City(CreateCity):
    id: uuid.UUID


class CreateUniversity(BaseModel):
    name: str
    short_name: str


class BaseInstitute(BaseModel):
    name: str


class CreateInstitute(BaseInstitute):
    university_id: uuid.UUID | None = None
    city_id: uuid.UUID


class Institute(BaseInstitute):
    id: uuid.UUID
    city: City


class UniversityBase(CreateUniversity):
    id: uuid.UUID


class University(UniversityBase):
    institutes: list[Institute]


class InstituteWithUniversity(Institute):
    university: University | None = None
