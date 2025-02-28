from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

# Replicate your enum in Pydantic for easy validation
class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LEAVE = "LEAVE"

class AttendanceBase(BaseModel):
    user_id: int
    date: date
    subject: str
    status: AttendanceStatus = AttendanceStatus.PRESENT

class AttendanceCreate(AttendanceBase):
    """Schema for creating a new attendance record."""
    pass

class AttendanceUpdate(BaseModel):
    """Schema for updating attendance (e.g., changing status)."""
    status: Optional[AttendanceStatus] = None

class AttendanceOut(BaseModel):
    """Schema for returning attendance data to the client."""
    id: int
    user_id: int
    date: date
    subject: str
    status: AttendanceStatus

    class Config:
        orm_mode = True
