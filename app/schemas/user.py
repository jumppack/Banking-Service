from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
