from pydantic import BaseModel
from typing import Optional

class JobDashboardResponse(BaseModel):
    job_id: int
    total_resumes: int
    strong_fit_count: int
    potential_count: int
    reject_count: int
    average_match_percentage: Optional[float] = None
    pending_screening_responses: int
