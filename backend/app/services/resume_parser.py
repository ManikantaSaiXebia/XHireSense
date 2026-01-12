from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
import sys
import os
import json
from app.services.ai_service import AIService
from app.models.resume import Resume, ResumeAnalysis, EmailStatus, BucketType

ai_service = None

# Force immediate output
def debug_print(msg):
    print(msg, flush=True)
    sys.stdout.flush()

def assign_bucket(match_percentage: float) -> BucketType:
    """Assign resume to bucket based on match percentage"""
    if match_percentage >= 80:
        return BucketType.STRONG_FIT
    elif match_percentage >= 60:
        return BucketType.POTENTIAL
    else:
        return BucketType.REJECT


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


def evaluateResume(jobDescription:str, resume:Resume, db: Session):
    """Reevaluates resume"""
    # Analyze resume with AI
    analysis_update = None
    current_ai_service = get_ai_service()
    debug_print(f"DEBUG: ai_service is {'available' if current_ai_service else 'None'}")
    if current_ai_service:
        try:
            debug_print("DEBUG: Starting AI analysis...")
            match_result = current_ai_service.analyze_resume_match(resume.extracted_text, jobDescription)
            debug_print(f"DEBUG: AI analysis result: {match_result}")
            if match_result:
                # Assign bucket based on match percentage
                bucket = assign_bucket(match_result.match_percentage)
                debug_print(f"DEBUG: Assigned bucket: {bucket}")
                resume.bucket = bucket

                # Create analysis record
                db_analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume.id).first()
                if not db_analysis:
                    return False

                setattr(db_analysis, "match_percentage", match_result.match_percentage)
                setattr(db_analysis, "matched_skills", json.dumps(match_result.matched_skills))
                setattr(db_analysis, "missing_skills", json.dumps(match_result.missing_skills))
                setattr(db_analysis, "bonus_skills", json.dumps(match_result.bonus_skills))
                setattr(db_analysis, "reasoning", match_result.reasoning)

                # Commit both bucket update and analysis
                db.commit()
                db.refresh(resume)
                db.refresh(db_analysis)
                debug_print("DEBUG: Analysis record created successfully")
            else:
                debug_print("DEBUG: AI analysis returned None")
        except Exception as e:
            debug_print(f"ERROR in AI analysis: {e}")
            import traceback
            traceback.print_exc()
            return False
            # Continue without analysis if AI fails
    else:
        debug_print("WARNING: GEMINI_API_KEY not set, skipping AI analysis")
        return False

    return True


class ResumeParser:
    @staticmethod
    def reevaluateAll(job_id:int, jobDescription:str) -> bool:
        """Reevaluates all the resumes again"""
        db_gen = get_db()
        db: Session = next(db_gen)

        try:
            resumes = (
                db.query(Resume)
                .filter(Resume.job_id == job_id)
                .all()
            )

            if not resumes:
                debug_print(f"DEBUG: Job not found - job_id: {job_id}")
                return False

            for resume in resumes:
                result = evaluateResume(jobDescription, resume, db)
                if not result:
                    return False
            print("Completed")
            return True

        finally:
            db.close()
        