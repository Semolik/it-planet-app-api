from datetime import datetime
import uuid
from pydantic import BaseModel
from schemas.files import ImageLink
from schemas.locations import Institution
from schemas.users import ChageOnApproveUserData, UserRead


class CreateVerificationRequest(ChageOnApproveUserData):
    institution_id: uuid.UUID


class VerificationRequest(BaseModel):
    id: uuid.UUID
    creation_date: datetime
    user_id: uuid.UUID
    user: UserRead
    updated_date: datetime | None
    reviewed: bool
    institution: Institution
    real_photo: ImageLink
    id_photo: ImageLink
    name: str
    birthdate: datetime
