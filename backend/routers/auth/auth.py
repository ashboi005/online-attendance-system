from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_db
from routers.auth.schemas import UserCreate
from models import User, TeacherSubject, UserRole
from sqlalchemy.future import select
from crud import get_user_by_email,get_user_by_clerkId
from typing import List

auth_router = APIRouter()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

@auth_router.post("/create-user")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_clerkId(db, user.clerkId)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(**user.dict())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@auth_router.delete("/delete-user/{clerkId}")
async def delete_user(clerkId: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.clerkId == clerkId))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}

@auth_router.get("/users/students")
async def get_students(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.role == "USER"))
    students = result.scalars().all()
    return students

@auth_router.get("/users/teachers")
async def get_teachers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.role == "TEACHER"))
    teachers = result.scalars().all()
    return teachers

@auth_router.get("/user/{clerkId}")
async def get_user(clerkId: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_clerkId(db, clerkId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@auth_router.post("/assign-subject/{teacherId}")
async def assign_subject_to_teacher(
    teacherId: str, 
    subject: str,  
    db: AsyncSession = Depends(get_db)
):
    teacher = await get_user_by_clerkId(db, teacherId)
    if not teacher:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Compare using the enum value
    if teacher.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="User is not a teacher")

    # Use teacher.clerkId, not teacher.id, because teacher_id in TeacherSubject is a string.
    teacher_subject = TeacherSubject(
        teacher_id=teacher.clerkId,
        subject=subject
    )
    db.add(teacher_subject)
    await db.commit()
    
    return {"message": "Subject assigned to teacher successfully"}
