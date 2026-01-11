import json
import sys
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.job import Job
from app.models.resume import Resume, ResumeAnalysis, EmailStatus, BucketType, EmailStatusEnum
from app.schemas.resume import (
    ResumeWithAnalysis, EmailStatusUpdate, EmailStatusResponse,
    ResumeResponse, ResumeAnalysisResponse, ResumeBatchUploadResponse
)
from app.services.pdf_service import PDFService
from app.services.ai_service import AIService
from app.services.email_service import EmailService
import os

# Force immediate output
def debug_print(msg):
    print(msg, flush=True)
    sys.stdout.flush()

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

pdf_service = PDFService()

# AI service will be initialized lazily when needed
# This avoids issues with environment variable loading order
ai_service = None

def get_ai_service():
    """Lazy initialization of AI service"""
    global ai_service
    if ai_service is None:
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                debug_print(f"DEBUG: GEMINI_API_KEY found (length: {len(gemini_key)}), initializing AIService...")
                ai_service = AIService()
                debug_print("DEBUG: AIService initialized successfully")
            else:
                debug_print("DEBUG: GEMINI_API_KEY not found, ai_service will be None")
        except Exception as e:
            debug_print(f"DEBUG: Error initializing AIService: {e}")
            import traceback
            traceback.print_exc()
    return ai_service

email_service = EmailService()
debug_print("DEBUG: Resume router module loaded")

def assign_bucket(match_percentage: float) -> BucketType:
    """Assign resume to bucket based on match percentage"""
    if match_percentage >= 80:
        return BucketType.STRONG_FIT
    elif match_percentage >= 60:
        return BucketType.POTENTIAL
    else:
        return BucketType.REJECT

@router.post("/upload", response_model=ResumeBatchUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    job_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload and analyze multiple resumes"""
    debug_print(f"DEBUG: Upload endpoint called - job_id: {job_id}, files count: {len(files)}")

    # Validate job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        debug_print(f"DEBUG: Job not found - job_id: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    debug_print(f"DEBUG: Job found - {job.title}")

    uploaded = []
    failed = []

    for file in files:
        try:
            debug_print(f"DEBUG: Processing file - {file.filename}")

            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                debug_print(f"DEBUG: Invalid file type - {file.filename}")
                failed.append({"filename": file.filename, "error": "Only PDF files are allowed"})
                continue

            # Read file content
            file_content = await file.read()
            debug_print(f"DEBUG: File read - size: {len(file_content)} bytes")

            # Extract text from PDF
            extracted_text = pdf_service.extract_text_from_pdf(file_content)
            debug_print(f"DEBUG: Extracted text length: {len(extracted_text) if extracted_text else 0}")
            if not extracted_text:
                failed.append({"filename": file.filename, "error": "Failed to extract text from PDF"})
                continue

            # Extract contact information
            name, email, phone = pdf_service.extract_contact_info(extracted_text)
            debug_print(f"DEBUG: Extracted contact info - name: {name}, email: {email}, phone: {phone}")

            # Create resume record (initially in REJECT bucket, will update after analysis)
            debug_print("DEBUG: Creating resume record in database...")
            db_resume = Resume(
                job_id=job_id,
                filename=file.filename,
                extracted_text=extracted_text,
                name=name,
                email=email,
                mobile=phone,
                bucket=BucketType.REJECT
            )
            db.add(db_resume)
            db.commit()
            db.refresh(db_resume)
            debug_print(f"DEBUG: Resume record created - id: {db_resume.id}")

            # Analyze resume with AI
            analysis_result = None
            current_ai_service = get_ai_service()
            debug_print(f"DEBUG: ai_service is {'available' if current_ai_service else 'None'}")
            if current_ai_service:
                try:
                    debug_print("DEBUG: Starting AI analysis...")
                    match_result = current_ai_service.analyze_resume_match(extracted_text, job.description)
                    debug_print(f"DEBUG: AI analysis result: {match_result}")
                    if match_result:
                        # Assign bucket based on match percentage
                        bucket = assign_bucket(match_result.match_percentage)
                        debug_print(f"DEBUG: Assigned bucket: {bucket}")
                        db_resume.bucket = bucket

                        # Create analysis record
                        db_analysis = ResumeAnalysis(
                            resume_id=db_resume.id,
                            match_percentage=match_result.match_percentage,
                            matched_skills=json.dumps(match_result.matched_skills),
                            missing_skills=json.dumps(match_result.missing_skills),
                            bonus_skills=json.dumps(match_result.bonus_skills),
                            reasoning=match_result.reasoning
                        )
                        db.add(db_analysis)
                        # Commit both bucket update and analysis
                        db.commit()
                        db.refresh(db_resume)
                        db.refresh(db_analysis)
                        analysis_result = db_analysis
                        debug_print("DEBUG: Analysis record created successfully")
                    else:
                        debug_print("DEBUG: AI analysis returned None")
                except Exception as e:
                    debug_print(f"ERROR in AI analysis: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continue without analysis if AI fails
            else:
                debug_print("WARNING: GEMINI_API_KEY not set, skipping AI analysis")

            # Create email status record
            db_email_status = EmailStatus(resume_id=db_resume.id)
            db.add(db_email_status)
            db.commit()
            db.refresh(db_email_status)

            db.refresh(db_resume)

            # Parse analysis skills if available
            analysis_response = None
            if analysis_result:
                analysis_response = ResumeAnalysisResponse(
                    id=analysis_result.id,
                    match_percentage=analysis_result.match_percentage,
                    matched_skills=json.loads(analysis_result.matched_skills),
                    missing_skills=json.loads(analysis_result.missing_skills),
                    bonus_skills=json.loads(analysis_result.bonus_skills),
                    reasoning=analysis_result.reasoning,
                    created_at=analysis_result.created_at
                )

            uploaded.append(ResumeWithAnalysis(
                resume=ResumeResponse(
                    id=db_resume.id,
                    job_id=db_resume.job_id,
                    filename=db_resume.filename,
                    name=db_resume.name,
                    email=db_resume.email,
                    mobile=db_resume.mobile,
                    bucket=db_resume.bucket,
                    uploaded_at=db_resume.uploaded_at
                ),
                analysis=analysis_response,
                email_status=EmailStatusResponse(
                    id=db_email_status.id,
                    status=db_email_status.status,
                    form_link=db_email_status.form_link,
                    sent_at=db_email_status.sent_at,
                    response_received_at=db_email_status.response_received_at
                )
            ))

        except Exception as e:
            debug_print(f"ERROR processing file {file.filename}: {e}")
            failed.append({"filename": file.filename, "error": str(e)})

    debug_print(f"DEBUG: Upload complete - uploaded: {len(uploaded)}, failed: {len(failed)}")

    return ResumeBatchUploadResponse(
        uploaded=uploaded,
        failed=failed
    )

@router.get("/job/{job_id}", response_model=List[ResumeWithAnalysis])
async def list_resumes(
    job_id: int,
    bucket: Optional[BucketType] = None,
    min_match: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """List all resumes for a job with optional filtering"""
    query = db.query(Resume).filter(Resume.job_id == job_id)
    
    if bucket:
        query = query.filter(Resume.bucket == bucket)
    
    # Join with ResumeAnalysis for sorting and filtering
    query = query.outerjoin(ResumeAnalysis, ResumeAnalysis.resume_id == Resume.id)
    
    if min_match is not None:
        query = query.filter(ResumeAnalysis.match_percentage >= min_match)
    
    # Default sort: highest match first
    resumes = query.order_by(
        ResumeAnalysis.match_percentage.desc().nullslast()
    ).all()
    
    result = []
    for resume in resumes:
        analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume.id).first()
        email_status = db.query(EmailStatus).filter(EmailStatus.resume_id == resume.id).first()
        
        analysis_response = None
        if analysis:
            analysis_response = ResumeAnalysisResponse(
                id=analysis.id,
                match_percentage=analysis.match_percentage,
                matched_skills=json.loads(analysis.matched_skills),
                missing_skills=json.loads(analysis.missing_skills),
                bonus_skills=json.loads(analysis.bonus_skills),
                reasoning=analysis.reasoning,
                created_at=analysis.created_at
            )
        
        email_status_response = None
        if email_status:
            email_status_response = EmailStatusResponse(
                id=email_status.id,
                status=email_status.status,
                form_link=email_status.form_link,
                sent_at=email_status.sent_at,
                response_received_at=email_status.response_received_at
            )
        
        result.append(ResumeWithAnalysis(
            resume=ResumeResponse(
                id=resume.id,
                job_id=resume.job_id,
                filename=resume.filename,
                name=resume.name,
                email=resume.email,
                mobile=resume.mobile,
                bucket=resume.bucket,
                uploaded_at=resume.uploaded_at
            ),
            analysis=analysis_response,
            email_status=email_status_response
        ))
    
    return result

@router.patch("/{resume_id}/bucket", response_model=ResumeResponse)
async def update_bucket(
    resume_id: int,
    bucket: BucketType,
    db: Session = Depends(get_db)
):
    """Manually override resume bucket"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    resume.bucket = bucket
    db.commit()
    db.refresh(resume)
    
    return ResumeResponse(
        id=resume.id,
        job_id=resume.job_id,
        filename=resume.filename,
        name=resume.name,
        email=resume.email,
        mobile=resume.mobile,
        bucket=resume.bucket,
        uploaded_at=resume.uploaded_at
    )

@router.post("/{resume_id}/send-screening-form", response_model=EmailStatusResponse)
async def send_screening_form(
    resume_id: int,
    candidate_email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Send screening form email to candidate"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    email_status = db.query(EmailStatus).filter(EmailStatus.resume_id == resume_id).first()
    if not email_status:
        email_status = EmailStatus(resume_id=resume_id)
        db.add(email_status)
        db.commit()
    
    job = db.query(Job).filter(Job.id == resume.job_id).first()
    
    # Send email
    form_link = email_service.get_form_link()
    success = await email_service.send_screening_form(
        candidate_email=candidate_email,
        job_title=job.title,
        form_link=form_link
    )
    
    if success:
        email_status.status = EmailStatusEnum.SENT
        email_status.form_link = form_link
        email_status.sent_at = datetime.now(timezone.utc)
        db.commit()
    
    db.refresh(email_status)
    
    return EmailStatusResponse(
        id=email_status.id,
        status=email_status.status,
        form_link=email_status.form_link,
        sent_at=email_status.sent_at,
        response_received_at=email_status.response_received_at
    )

@router.patch("/{resume_id}/email-status", response_model=EmailStatusResponse)
async def update_email_status(
    resume_id: int,
    status_update: EmailStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update email status (e.g., mark as response received)"""
    email_status = db.query(EmailStatus).filter(EmailStatus.resume_id == resume_id).first()
    if not email_status:
        raise HTTPException(status_code=404, detail="Email status not found")

    email_status.status = status_update.status
    if status_update.form_link:
        email_status.form_link = status_update.form_link

    if status_update.status == EmailStatusEnum.RESPONSE_RECEIVED:
        email_status.response_received_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(email_status)

    return EmailStatusResponse(
        id=email_status.id,
        status=email_status.status,
        form_link=email_status.form_link,
        sent_at=email_status.sent_at,
        response_received_at=email_status.response_received_at
    )

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Delete a resume and all associated data"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Delete the resume (cascade will handle related records)
    db.delete(resume)
    db.commit()

    return {"message": "Resume deleted successfully"}
