from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr
from fastapi_users.schemas import BaseUserCreate, BaseUser, BaseUserUpdate


class BaseUserEmail(BaseModel):
    email: EmailStr


class CustomUserFields(BaseModel):
    name: str
    birthdate: datetime | None = None
    register_date: datetime


class UserRead(BaseUser[uuid.UUID], CustomUserFields):
    pass


class UserReadWithEmail(UserRead, BaseUserEmail):
    pass


class UserReadShort(BaseUser):
    id: uuid.UUID


class UserReadShortWithEmail(UserReadShort, BaseUserEmail):
    pass


class UserCreate(BaseUserCreate, CustomUserFields):
    pass


class UserUpdate(BaseUserUpdate, CustomUserFields):
    pass
