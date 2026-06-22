import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Role(str, enum.Enum):
    VENDOR = "vendor"
    ELECTRICIAN = "electrician"
    PLANNER = "planner"


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(SAEnum(Role), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship("Application", back_populates="applicant", foreign_keys="Application.applicant_id")
    reviewed_applications = relationship("Application", back_populates="reviewer", foreign_keys="Application.reviewer_id")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    stall_number = Column(String(20), nullable=False, index=True)
    stall_area = Column(String(50), nullable=False, index=True)
    peak_kw = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    has_open_flame = Column(Boolean, default=False, nullable=False)
    status = Column(SAEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False, index=True)
    reject_reason = Column(Text, nullable=True)
    meter_number = Column(String(50), nullable=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    reviewed_at = Column(DateTime, nullable=True)

    applicant = relationship("User", back_populates="applications", foreign_keys=[applicant_id])
    reviewer = relationship("User", back_populates="reviewed_applications", foreign_keys=[reviewer_id])
