from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.resume import BucketType, EmailStatusEnum

class ResumeUpload(BaseModel):
    job_id: int

class ResumeResponse(BaseModel):
    id: int
    job_id: int
    filename: str
    bucket: BucketType
    uploaded_at: datetime

    class Config:
        from_attributes = True

class ResumeAnalysisResponse(BaseModel):
    id: int
    match_percentage: float
    matched_skills: list[str]
    missing_skills: list[str]
    bonus_skills: list[str]
    reasoning: str
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeWithAnalysis(BaseModel):
    resume: ResumeResponse
    analysis: Optional[ResumeAnalysisResponse] = None
    email_status: Optional["EmailStatusResponse"] = None

    class Config:
        from_attributes = True

class ResumeBatchUploadResponse(BaseModel):
    uploaded: List[ResumeWithAnalysis]
    failed: List[dict]  # List of {"filename": str, "error": str}

    class Config:
        from_attributes = True

class EmailStatusUpdate(BaseModel):
    status: EmailStatusEnum
    form_link: Optional[str] = None

class EmailStatusResponse(BaseModel):
    id: int
    status: EmailStatusEnum
    form_link: Optional[str] = None
    sent_at: Optional[datetime] = None
    response_received_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Update forward reference
ResumeWithAnalysis.model_rebuild()
