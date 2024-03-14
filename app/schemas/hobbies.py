from uuid import UUID
from pydantic import BaseModel


class CreateHobby(BaseModel):
    name: str


class Hobby(CreateHobby):
    id: UUID

    class Config:
        from_attributes = True


class HobbyWithLike(Hobby):
    liked: bool = False

    class Config:
        from_attributes = True
