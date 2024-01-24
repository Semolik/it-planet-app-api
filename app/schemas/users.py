from datetime import datetime
import re
import uuid
from pydantic import BaseModel, EmailStr
from fastapi_users.schemas import BaseUserCreate, BaseUser, BaseUserUpdate
from pydantic_core import core_schema

from schemas.files import ImageLink


class BaseUserEmail(BaseModel):
    email: EmailStr


class CustomUserFields(BaseModel):
    name: str
    birthdate: datetime | None = None
    register_date: datetime
    discription: str


class CustomUserFieldsRead(BaseModel):
    image: ImageLink | None = None


class UserRead(BaseUser[uuid.UUID], CustomUserFields, CustomUserFieldsRead):
    pass


class UserReadWithEmail(UserRead, BaseUserEmail):
    pass


class UserReadShort(BaseUser, CustomUserFieldsRead):
    id: uuid.UUID


class UserReadShortWithEmail(UserReadShort, BaseUserEmail):
    pass


class UserCreate(BaseUserCreate, CustomUserFields):
    pass


class UserUpdate(BaseUserUpdate, CustomUserFields):
    pass
