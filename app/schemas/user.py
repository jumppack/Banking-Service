from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="The user's email address, used for login.", example="john.doe@example.com")
    is_active: bool = Field(default=True, description="Whether the user account is active and can log in.")

class UserCreate(UserBase):
    password: str = Field(..., description="The user's raw password. Will be hashed securely before storage.", min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="New email address for the account holder.")

class UserResponse(UserBase):
    id: UUID = Field(..., description="The unique internal UUID of the user.")
    model_config = ConfigDict(from_attributes=True)
