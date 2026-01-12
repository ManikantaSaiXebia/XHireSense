from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    jobs: list[JobResponse]
