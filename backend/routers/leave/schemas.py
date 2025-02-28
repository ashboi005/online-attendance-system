from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum

class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class LeaveBase(BaseModel):
    student_id: str          
    teacher_subject_id: str
    date: date
    half_day: bool = False
    reason: Optional[str] = None

class LeaveCreate(LeaveBase):
    """Schema for creating a new leave request."""
    pass

class LeaveUpdate(BaseModel):
    """Schema for updating a leave request status."""
    status: LeaveStatus

class LeaveOut(LeaveBase):
    id: int
    status: LeaveStatus

    class Config:
        from_attributes = True
