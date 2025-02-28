from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserCreate(BaseModel):
    clerkId: str
    user_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    role: Optional[str] = "USER"

class UserRole(str, Enum):
    USER = "USER"
    TEACHER = "TEACHER"

class UserOut(BaseModel):
    clerkId: str
    user_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    role: UserRole

    class Config:
        from_attributes = True