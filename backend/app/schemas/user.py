import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, UserStatus


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: UserRole
    status: UserStatus
    created_at: datetime

    model_config = {"from_attributes": True}
