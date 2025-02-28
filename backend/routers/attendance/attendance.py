from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime

from config import get_db
from models import Attendance, AttendanceStatus, User
from .schemas import AttendanceCreate, AttendanceUpdate, AttendanceOut

attendance_router = APIRouter()

@attendance_router.post("/", response_model=AttendanceOut)
async def create_attendance(
    attendance_data: AttendanceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new attendance record.
    It looks up the User by attendance_data.user_id and then sets the attendance record's clerkId 
    from the associated User.
    """
    # Query the User table using the provided user_id
    result = await db.execute(select(User).filter(User.user_id == attendance_data.user_id))
    user_obj = result.scalars().first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create the attendance record, populating clerkId from the found User
    new_attendance = Attendance(
        user_id=attendance_data.user_id,
        clerkId=user_obj.clerkId,
        date=datetime.now().date(),
        status=attendance_data.status,
        subject=attendance_data.subject
    )
    db.add(new_attendance)
    await db.commit()
    await db.refresh(new_attendance)
    return new_attendance


@attendance_router.get("/", response_model=List[AttendanceOut])
async def list_attendance(db: AsyncSession = Depends(get_db)):
    """List all attendance records."""
    result = await db.execute(select(Attendance))
    attendances = result.scalars().all()
    return attendances


@attendance_router.put("/{attendance_id}", response_model=AttendanceOut)
async def update_attendance(
    attendance_id: int,
    update_data: AttendanceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing attendance record (e.g. change status)."""
    attendance = await db.get(Attendance, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    if update_data.status is not None:
        attendance.status = update_data.status
    db.add(attendance)
    await db.commit()
    await db.refresh(attendance)
    return attendance

@attendance_router.delete("/{attendance_id}")
async def delete_attendance(attendance_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an attendance record."""
    attendance = await db.get(Attendance, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    await db.delete(attendance)
    await db.commit()
    return {"detail": "Attendance record deleted successfully"}

@attendance_router.get("/user/{clerk_id}", response_model=List[AttendanceOut])
async def get_attendance_by_clerk_id(clerk_id: str, db: AsyncSession = Depends(get_db)):
    """Get attendance records by clerk ID."""
    result = await db.execute(select(Attendance).where(Attendance.user_id == clerk_id))
    attendances = result.scalars().all()
    if not attendances:
        raise HTTPException(status_code=404, detail="No attendance records found for the given clerk ID")
    return attendances

