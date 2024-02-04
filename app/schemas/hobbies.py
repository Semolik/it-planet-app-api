from uuid import UUID
from pydantic import BaseModel


class CreateHobby(BaseModel):
    name: str


class Hobby(CreateHobby):
    id: UUID