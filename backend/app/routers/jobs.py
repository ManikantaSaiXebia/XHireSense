from app.services.resume_parser import ResumeParser
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse, JobListResponse, JobUpdate
from app.schemas.dashboard import JobDashboardResponse
from app.models.resume import Resume, ResumeAnalysis, EmailStatus, BucketType, EmailStatusEnum
from sqlalchemy import func, case

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create a new job posting"""
    db_job = Job(title=job.title, description=job.description)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.get("/", response_model=JobListResponse)
async def list_jobs(db: Session = Depends(get_db)):
    """List all jobs"""
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return JobListResponse(jobs=jobs)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    """Update a job posting and re-evaluate all associated resumes"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_codeew=404, detail="Job not found")

    # Update job fields if provided
    update_data = job_update.dict(exclude_unset=True)
    if update_data:
        for field, value in update_data.items():
            setattr(job, field, value)

    # Commit job update
    db.commit()
    db.refresh(job)

    ResumeParser.reevaluateAll(job_id, job_update.description)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job and all associated resumes"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    try:
        db.delete(job)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )
    
    return None

@router.get("/{job_id}/dashboard", response_model=JobDashboardResponse)
async def get_job_dashboard(job_id: int, db: Session = Depends(get_db)):
    """Get dashboard statistics for a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Total resumes
    total_resumes = db.query(Resume).filter(Resume.job_id == job_id).count()
    
    # Bucket counts
    strong_fit_count = db.query(Resume).filter(
        Resume.job_id == job_id,
        Resume.bucket == BucketType.STRONG_FIT
    ).count()
    
    potential_count = db.query(Resume).filter(
        Resume.job_id == job_id,
        Resume.bucket == BucketType.POTENTIAL
    ).count()
    
    reject_count = db.query(Resume).filter(
        Resume.job_id == job_id,
        Resume.bucket == BucketType.REJECT
    ).count()
    
    # Average match percentage
    avg_match = db.query(func.avg(ResumeAnalysis.match_percentage)).join(
        Resume, ResumeAnalysis.resume_id == Resume.id
    ).filter(Resume.job_id == job_id).scalar()
    
    # Pending screening responses (emails sent but no response)
    pending_count = db.query(EmailStatus).join(
        Resume, EmailStatus.resume_id == Resume.id
    ).filter(
        Resume.job_id == job_id,
        EmailStatus.status == EmailStatusEnum.SENT
    ).count()
    
    return JobDashboardResponse(
        job_id=job_id,
        total_resumes=total_resumes,
        strong_fit_count=strong_fit_count,
        potential_count=potential_count,
        reject_count=reject_count,
        average_match_percentage=float(avg_match) if avg_match else None,
        pending_screening_responses=pending_count
    )
