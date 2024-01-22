from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr
from fastapi_users.schemas import BaseUserCreate, BaseUser, BaseUserUpdate
from pydantic_core import core_schema

from schemas.files import ImageLink


class ISOdate(datetime):
    @classmethod
    def validate(cls, v: datetime, handler) -> str | None:
        if not v:
            return None
        if isinstance(v, str):  # regex test
            return v
        if not isinstance(v, datetime):
            raise TypeError('ISOdate must be datetime (model)')
        return v.isoformat().split('T')[0]

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, _handler) -> core_schema.CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )


class BaseUserEmail(BaseModel):
    email: EmailStr


class CustomUserFields(BaseModel):
    name: str
    birthdate: ISOdate | None = None
    register_date: ISOdate


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
