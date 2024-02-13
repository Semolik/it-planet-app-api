from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class Notification(BaseModel):
    id: UUID
    message: str
    header: str
    read: bool
    creation_date: datetime
