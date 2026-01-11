from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class BucketType(str, enum.Enum):
    STRONG_FIT = "STRONG_FIT"
    POTENTIAL = "POTENTIAL"
    REJECT = "REJECT"

class EmailStatusEnum(str, enum.Enum):
    NOT_SENT = "NOT_SENT"
    SENT = "SENT"
    RESPONSE_RECEIVED = "RESPONSE_RECEIVED"

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    mobile = Column(String(50), nullable=True)
    bucket = Column(SQLEnum(BucketType), nullable=False, default=BucketType.REJECT, index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="resumes")
    analysis = relationship("ResumeAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    email_status = relationship("EmailStatus", back_populates="resume", uselist=False, cascade="all, delete-orphan")

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, unique=True, index=True)
    match_percentage = Column(Float, nullable=False)
    matched_skills = Column(Text, nullable=False)  # JSON array stored as text
    missing_skills = Column(Text, nullable=False)  # JSON array stored as text
    bonus_skills = Column(Text, nullable=False)  # JSON array stored as text
    reasoning = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="analysis")

class EmailStatus(Base):
    __tablename__ = "email_statuses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, unique=True, index=True)
    status = Column(SQLEnum(EmailStatusEnum), nullable=False, default=EmailStatusEnum.NOT_SENT)
    form_link = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    response_received_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    resume = relationship("Resume", back_populates="email_status")
