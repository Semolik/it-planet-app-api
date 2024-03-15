from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr
from fastapi_users.schemas import BaseUserCreate, BaseUser, BaseUserUpdate
from schemas.locations import Institution
from schemas.hobbies import Hobby

from schemas.files import ImageLink


class BaseUserEmail(BaseModel):
    email: EmailStr


class CustomUserFieldsWithoutDates(BaseModel):
    name: str
    description: str = ''


class ChageOnApproveUserData(BaseModel):
    name: str
    birthdate: datetime


class CustomUserFields(CustomUserFieldsWithoutDates):
    birthdate: datetime
    verified: bool


class CustomUserFieldsReadWithotHobbies(BaseModel):
    image: ImageLink | None = None
    age: int
    register_date: datetime


class CustomUserFieldsRead(CustomUserFieldsReadWithotHobbies):
    hobbies: list[Hobby]


class UserReadAfterRegister(BaseUser[uuid.UUID], CustomUserFields, CustomUserFieldsReadWithotHobbies):
    pass


class UserRead(UserReadAfterRegister, CustomUserFieldsRead):
    pass


class UserReadWithEmail(UserRead, BaseUserEmail):
    pass


class UserReadInstitution(UserReadWithEmail):
    institution: Institution | None


class UserReadShort(CustomUserFieldsRead, CustomUserFieldsWithoutDates):
    id: uuid.UUID


class UserReadShortWithEmail(UserReadShort, BaseUserEmail):
    pass


class UserCreate(BaseUserCreate, CustomUserFields):
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
