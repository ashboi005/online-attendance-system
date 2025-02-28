import enum
import datetime
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserRole(enum.Enum):
    USER = "USER"
    TEACHER = "TEACHER"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    clerkId = Column(String, unique=True, nullable=False)
    user_id = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    attendance_records = relationship("Attendance", back_populates="user", cascade="all, delete-orphan",foreign_keys=lambda: [Attendance.clerkId])
    teacher_subject = relationship("TeacherSubject", back_populates="teacher", uselist=False)
    leaves = relationship("Leave", back_populates="student", cascade="all, delete-orphan")

class AttendanceStatus(enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LEAVE = "LEAVE"  

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    clerkId = Column(String, ForeignKey("users.clerkId"), nullable=False)
    date = Column(Date, nullable=False)
    subject = Column(String, nullable=False)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT, nullable=False)

    user = relationship("User", back_populates="attendance_records", foreign_keys=[clerkId])

class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"
    teacher_id = Column(String, ForeignKey("users.clerkId"), primary_key=True, nullable=False)
    subject = Column(String, nullable=False)

    teacher = relationship("User", back_populates="teacher_subject", uselist=False)
    leaves = relationship("Leave", back_populates="teacher_subject", cascade="all, delete-orphan")


class LeaveStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Leave(Base):
    __tablename__ = "leaves"
    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(String, ForeignKey("users.clerkId"), nullable=False)
    teacher_subject_id = Column(String, ForeignKey("teacher_subjects.teacher_id"), nullable=False)
    date = Column(Date, nullable=False)
    half_day = Column(Boolean, default=False)
    reason = Column(String, nullable=True)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)

    student = relationship("User", back_populates="leaves")
    teacher_subject = relationship("TeacherSubject", back_populates="leaves")

