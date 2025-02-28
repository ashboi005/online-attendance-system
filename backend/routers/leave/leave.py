from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from config import get_db
from models import Leave, TeacherSubject, User, LeaveStatus
from routers.leave.schemas import LeaveCreate, LeaveUpdate, LeaveOut

leave_router = APIRouter()

@leave_router.post("/", response_model=LeaveOut)
async def apply_leave(
    leave_data: LeaveCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    A student applies for a leave for a specific teacher–subject.
    The leave_data.student_id and leave_data.teacher_subject_id are both strings (the unique clerkIds).
    """
    # Verify that the teacher–subject association exists.
    teacher_subject = await db.get(TeacherSubject, leave_data.teacher_subject_id)
    if not teacher_subject:
        raise HTTPException(status_code=404, detail="Teacher subject not found")
    
    # Verify that the student exists.
    student_query = await db.execute(select(User).filter(User.clerkId == leave_data.student_id))
    student = student_query.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    new_leave = Leave(
        student_id=leave_data.student_id,
        teacher_subject_id=leave_data.teacher_subject_id,  # teacher_subject_id is the teacher's clerkId
        date=leave_data.date,
        half_day=leave_data.half_day,
        reason=leave_data.reason,
        status=LeaveStatus.PENDING
    )
    db.add(new_leave)
    await db.commit()
    await db.refresh(new_leave)
    return new_leave

@leave_router.get("/", response_model=List[LeaveOut])
async def list_leaves(db: AsyncSession = Depends(get_db)):
    """
    List all leave requests.
    """
    result = await db.execute(select(Leave))
    return result.scalars().all()

@leave_router.get("/user/{clerk_id}", response_model=List[LeaveOut])
async def get_user_leaves(clerk_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get all leaves by student clerkId or teacher clerkId.
    """
    teacher_subjects = await db.execute(
        select(TeacherSubject).filter(TeacherSubject.teacher_id == clerk_id)
    )
    teacher_subject_ids = [ts.teacher_id for ts in teacher_subjects.scalars().all()]

    result = await db.execute(
        select(Leave).filter(
            (Leave.student_id == clerk_id) | 
            (Leave.teacher_subject_id.in_(teacher_subject_ids))
        )
    )
    return result.scalars().all()

@leave_router.get("/{leave_id}", response_model=LeaveOut)
async def get_leave(leave_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a specific leave request by its ID.
    """
    leave = await db.get(Leave, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    return leave

@leave_router.put("/{leave_id}", response_model=LeaveOut)
async def update_leave_status(
    leave_id: int,
    update_data: LeaveUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Allow a teacher to approve or reject a leave request.
    """
    leave = await db.get(Leave, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    leave.status = update_data.status
    db.add(leave)
    await db.commit()
    await db.refresh(leave)
    return leave

@leave_router.delete("/{leave_id}")
async def delete_leave(leave_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a leave request.
    """
    leave = await db.get(Leave, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    await db.delete(leave)
    await db.commit()
    return {"detail": "Leave deleted successfully"}
