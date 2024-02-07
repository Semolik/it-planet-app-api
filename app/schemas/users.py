from datetime import datetime
import re
import uuid
from pydantic import BaseModel, EmailStr
from fastapi_users.schemas import BaseUserCreate, BaseUser, BaseUserUpdate
from pydantic_core import core_schema

from schemas.files import ImageLink


class BaseUserEmail(BaseModel):
    email: EmailStr


class CustomUserFieldsWithoutDates(BaseModel):
    name: str
    discription: str = ''
    verified: bool


class CustomUserFields(CustomUserFieldsWithoutDates):
    birthdate: datetime | None = None
    register_date: datetime


class CustomUserFieldsRead(BaseModel):
    image: ImageLink | None = None
    age: int


class UserRead(BaseUser[uuid.UUID], CustomUserFields, CustomUserFieldsRead):
    pass


class UserReadWithEmail(UserRead, BaseUserEmail):
    pass


class UserReadShort(CustomUserFieldsRead, CustomUserFieldsWithoutDates):
    id: uuid.UUID


class UserReadShortWithEmail(UserReadShort, BaseUserEmail):
    pass


class UserCreate(BaseUserCreate, CustomUserFields):
    pass


class UserUpdate(BaseUserUpdate, CustomUserFields):
    pass


class UserLike(BaseModel):
    user_id: uuid.UUID
    liked_user_id: uuid.UUID
    like: bool
    is_match: bool = False
