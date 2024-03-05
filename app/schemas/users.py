from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr
from fastapi_users.schemas import BaseUserCreate, BaseUser, BaseUserUpdate
from schemas.hobbies import Hobby

from schemas.files import ImageLink


class BaseUserEmail(BaseModel):
    email: EmailStr


class CustomUserFieldsWithoutDates(BaseModel):
    name: str
    discription: str = ''
    verified: bool


class ChageOnApproveUserData(BaseModel):
    name: str
    birthdate: datetime


class CustomUserFields(CustomUserFieldsWithoutDates):
    birthdate: datetime
    register_date: datetime


class CustomUserFieldsRead(BaseModel):
    image: ImageLink | None = None
    age: int
    hobbies: list[Hobby]


class UserRead(BaseUser[uuid.UUID], CustomUserFields, CustomUserFieldsRead):
    pass


class UserReadWithEmail(UserRead, BaseUserEmail):
    pass


class UserReadShort(CustomUserFieldsRead, CustomUserFieldsWithoutDates):
    id: uuid.UUID

    class Config:
        from_attributes = True


class UserReadShortWithEmail(UserReadShort, BaseUserEmail):
    pass


class UserCreate(BaseUserCreate):
    birthdate: datetime


class UserUpdate(BaseUserUpdate, CustomUserFields):
    pass


class UserLike(BaseModel):
    user_id: uuid.UUID
    liked_user_id: uuid.UUID
    like: bool
    is_match: bool = False


class UserLikeFull(BaseModel):
    is_match: bool = False
    liked_user: UserReadShort
