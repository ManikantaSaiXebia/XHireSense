import json
import os
import google.generativeai as genai
from typing import Dict, Optional
from pydantic import BaseModel

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class MatchResult(BaseModel):
    match_percentage: float
    matched_skills: list[str]
    missing_skills: list[str]
    bonus_skills: list[str]
    reasoning: str

class AIService:
    """Service for AI-powered resume matching using Google Gemini"""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_resume_match(
        self, 
        resume_text: str, 
        job_description: str
    ) -> Optional[MatchResult]:
        """
        Analyze resume against job description using Gemini
        
        Args:
            resume_text: Extracted text from resume PDF
            job_description: Job description text
            
        Returns:
            MatchResult with match percentage and explainable details
        """
        prompt = self._build_prompt(resume_text, job_description)
        
        # Retry logic for malformed JSON
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Try to extract JSON from response
                json_text = self._extract_json(response_text)
                result_dict = json.loads(json_text)
                
                # Validate structure
                if not self._validate_result(result_dict):
                    if attempt < max_retries - 1:
                        continue
                    raise ValueError("Invalid result structure")
                
                return MatchResult(**result_dict)
                
            except Exception as e:
                if attempt < max_retries - 1:
                    continue
                print(f"Error in AI analysis (attempt {attempt + 1}): {e}")
                return None
        
        return None
    
    def _build_prompt(self, resume_text: str, job_description: str) -> str:
        """Build the prompt for Gemini with explicit JSON format requirement"""
        prompt = f"""You are an expert hiring assistant. Analyze the resume against the job description and provide a detailed match analysis.

JOB DESCRIPTION:
{job_description}

RESUME TEXT:
{resume_text}

SCORING RUBRIC:
- Core required skills have HIGH weight (40-50% of score)
- Nice-to-have skills have MEDIUM weight (20-30% of score)
- Experience alignment matters (20-30% of score)
- Missing critical skills MUST reduce score significantly
- Be CONSERVATIVE and REALISTIC in scoring

Return ONLY valid JSON in this EXACT format (no markdown, no prose, no additional text):
{{
  "match_percentage": <number between 0 and 100>,
  "matched_skills": [<array of matched skill strings>],
  "missing_skills": [<array of missing critical skill strings>],
  "bonus_skills": [<array of bonus/nice-to-have skills found>],
  "reasoning": "<2-3 sentence explanation of the match>"
}}

JSON:"""
        return prompt
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from response text (handles code blocks, etc.)"""
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        
        # Find JSON object boundaries
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        
        if start_idx != -1 and end_idx > start_idx:
            return text[start_idx:end_idx]
        
        return text
    
    def _validate_result(self, result_dict: Dict) -> bool:
        """Validate that result has all required fields with correct types"""
        required_fields = {
            "match_percentage": (int, float),
            "matched_skills": list,
            "missing_skills": list,
            "bonus_skills": list,
            "reasoning": str
        }
        
        for field, expected_type in required_fields.items():
            if field not in result_dict:
                return False
            
            value = result_dict[field]
            if field == "match_percentage":
                if not isinstance(value, (int, float)) or not (0 <= value <= 100):
                    return False
            elif field == "reasoning":
                if not isinstance(value, str):
                    return False
            else:  # skills arrays
                if not isinstance(value, list) or not all(isinstance(s, str) for s in value):
                    return False
        
        return True
