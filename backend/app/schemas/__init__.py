from .job import JobCreate, JobResponse, JobListResponse
from .resume import (
    ResumeUpload, ResumeResponse, ResumeAnalysisResponse,
    ResumeWithAnalysis, EmailStatusUpdate, EmailStatusResponse
)
from .dashboard import JobDashboardResponse

__all__ = [
    "JobCreate", "JobResponse", "JobListResponse",
    "ResumeUpload", "ResumeResponse", "ResumeAnalysisResponse",
    "ResumeWithAnalysis", "EmailStatusUpdate", "EmailStatusResponse",
    "JobDashboardResponse"
]
