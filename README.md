# XHireSense

**Explainable AI for Smarter Hiring Decisions**

XHireSense is a complete, production-ready web application that uses Google Gemini AI to analyze resumes against job descriptions, providing explainable match scores and intelligent candidate bucketing.

## Architecture Overview

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.10
- **Database**: SQLite with SQLAlchemy ORM
- **AI Service**: Google Gemini API for resume matching
- **PDF Processing**: PyPDF2 for text extraction
- **Email Service**: Mock implementation (ready for production integration)

### Frontend (Next.js)
- **Framework**: Next.js 24.12.0 with App Router
- **Styling**: Custom CSS with modern design
- **State Management**: React hooks
- **API Client**: Fetch API for backend communication

## Key Features

1. **Job Management**
   - Create and manage job postings
   - View all jobs on landing page
   - Job descriptions support Markdown

2. **Resume Upload & Processing**
   - Upload PDF resumes (multiple per job)
   - Automatic text extraction from PDFs
   - Resume storage and association with jobs

3. **AI-Powered Resume Matching**
   - Google Gemini analyzes resume against job description
   - Returns structured JSON with:
     - Match percentage (0-100)
     - Matched skills
     - Missing skills
     - Bonus skills
     - AI reasoning
   - Retry logic for malformed responses
   - Graceful error handling

4. **Smart Candidate Bucketing**
   - Automatic bucket assignment:
     - **STRONG_FIT**: match >= 80%
     - **POTENTIAL**: match 60-79%
     - **REJECT**: match < 60%
   - Manual override capability
   - Server-side bucket logic

5. **Explainable AI UI**
   - Match percentage display
   - Color-coded bucket labels
   - Skills breakdown:
     - ✔ Matched skills (green)
     - ⚠ Missing skills (yellow)
     - ⭐ Bonus skills (purple)
   - AI reasoning explanation (2-3 lines)

6. **Dashboard**
   - Total resume count
   - Bucket distribution (Strong/Potential/Reject)
   - Average match percentage
   - Pending screening responses

7. **Email Integration**
   - Send screening forms to candidates
   - Track email status (NOT_SENT, SENT, RESPONSE_RECEIVED)
   - Microsoft Form link support

8. **Filtering & Sorting**
   - Filter by bucket
   - Filter by minimum match percentage
   - Default sort: highest match first

## Project Structure

```
XHireSense/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # Database models
│   │   │   ├── __init__.py
│   │   │   ├── job.py
│   │   │   └── resume.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── job.py
│   │   │   ├── resume.py
│   │   │   └── dashboard.py
│   │   ├── routers/             # API routes
│   │   │   ├── __init__.py
│   │   │   ├── jobs.py
│   │   │   └── resumes.py
│   │   └── services/            # Business logic
│   │       ├── __init__.py
│   │       ├── ai_service.py    # Gemini AI integration
│   │       ├── pdf_service.py   # PDF text extraction
│   │       └── email_service.py # Email handling
│   ├── requirements.txt
│   └── xhiresense.db            # SQLite database (created on first run)
│
└── frontend/
    ├── app/
    │   ├── layout.tsx           # Root layout
    │   ├── page.tsx             # Landing page (job list)
    │   ├── jobs/
    │   │   ├── page.tsx         # Create job page
    │   │   └── [id]/
    │   │       └── page.tsx     # Job detail page
    │   └── globals.css          # Global styles
    ├── lib/
    │   └── api.ts               # API client
    ├── package.json
    ├── tsconfig.json
    ├── next.config.js
    └── .env.local               # Environment variables
```

## Database Schema

### Jobs Table
- `id` (Primary Key)
- `title` (String)
- `description` (Text)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Resumes Table
- `id` (Primary Key)
- `job_id` (Foreign Key → Jobs)
- `filename` (String)
- `extracted_text` (Text)
- `bucket` (Enum: STRONG_FIT, POTENTIAL, REJECT)
- `uploaded_at` (DateTime)

### Resume Analyses Table
- `id` (Primary Key)
- `resume_id` (Foreign Key → Resumes, Unique)
- `match_percentage` (Float)
- `matched_skills` (Text - JSON array)
- `missing_skills` (Text - JSON array)
- `bonus_skills` (Text - JSON array)
- `reasoning` (Text)
- `created_at` (DateTime)

### Email Statuses Table
- `id` (Primary Key)
- `resume_id` (Foreign Key → Resumes, Unique)
- `status` (Enum: NOT_SENT, SENT, RESPONSE_RECEIVED)
- `form_link` (Text, Nullable)
- `sent_at` (DateTime, Nullable)
- `response_received_at` (DateTime, Nullable)

## AI Flow

1. **Resume Upload**
   - User uploads PDF file
   - Backend extracts text using PyPDF2
   - Resume record created in database

2. **AI Analysis**
   - Job description and resume text sent to Gemini
   - Prompt includes:
     - Full job description
     - Full resume text
     - Explicit scoring rubric
     - JSON format requirement
   - Gemini returns structured JSON:
     ```json
     {
       "match_percentage": 85.5,
       "matched_skills": ["Python", "FastAPI", "SQL"],
       "missing_skills": ["Docker", "Kubernetes"],
       "bonus_skills": ["Machine Learning"],
       "reasoning": "Strong technical background with relevant experience..."
     }
     ```

3. **Bucket Assignment**
   - Server-side logic assigns bucket based on match percentage
   - Record stored in database

4. **Error Handling**
   - If JSON is malformed, retry once
   - If still invalid, resume saved without analysis
   - Logs errors for debugging

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ (for Next.js)
- Google Gemini API Key

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variable**
   ```bash
   # On Windows (PowerShell):
   $env:GEMINI_API_KEY="your-api-key-here"
   
   # On macOS/Linux:
   export GEMINI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file in the backend directory:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

5. **Run the backend server**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   Server will start on `http://localhost:8000`
   API docs available at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure API URL** (if different from default)
   Edit `frontend/.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```
   
   Frontend will start on `http://localhost:3000`

## Usage

1. **Create a Job**
   - Navigate to the landing page
   - Click "Create New Job"
   - Enter job title and description (Markdown supported)
   - Submit to create job

2. **Upload Resumes**
   - Click on a job to open detail page
   - Click "Upload Resume"
   - Select PDF file
   - Resume is automatically analyzed by AI

3. **Review Candidates**
   - View match percentages and bucket assignments
   - Review matched/missing/bonus skills
   - Read AI reasoning for each candidate
   - Filter by bucket or sort by match score

4. **Manage Candidates**
   - Manually override bucket assignment
   - Send screening forms to candidates
   - Track email status

5. **Monitor Dashboard**
   - View job-level statistics
   - Track bucket distribution
   - Monitor average match percentage
   - Check pending screening responses

## Configuration

### Environment Variables

**Backend:**
- `GEMINI_API_KEY` (Required): Google Gemini API key
- `DATABASE_URL` (Optional): SQLite database path (default: `sqlite:///./xhiresense.db`)
- `MICROSOFT_FORM_LINK` (Optional): Default Microsoft Form link for screening

**Frontend:**
- `NEXT_PUBLIC_API_URL` (Optional): Backend API URL (default: `http://localhost:8000`)

## Production Considerations

1. **Database**
   - Current implementation uses SQLite (file-based)
   - For production, consider PostgreSQL or MySQL
   - Update `DATABASE_URL` in database.py

2. **Email Service**
   - Current implementation is a mock
   - Integrate with SMTP (aiosmtplib) or SendGrid/Mailgun
   - Update `email_service.py`

3. **File Storage**
   - Currently stores extracted text only
   - For production, consider storing PDFs (S3, Azure Blob, etc.)
   - Update resume upload logic

4. **API Security**
   - Add authentication/authorization
   - Implement rate limiting
   - Add CORS configuration for production domains

5. **Error Handling**
   - Add comprehensive logging
   - Implement error tracking (Sentry, etc.)
   - Add monitoring and alerts

6. **Performance**
   - Add database indexing (already included for key fields)
   - Consider caching for frequently accessed data
   - Optimize AI API calls (batch processing, etc.)

## API Endpoints

### Jobs
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create job
- `GET /api/jobs/{id}` - Get job details
- `DELETE /api/jobs/{id}` - Delete job
- `GET /api/jobs/{id}/dashboard` - Get job dashboard stats

### Resumes
- `POST /api/resumes/upload` - Upload and analyze resume
- `GET /api/resumes/job/{job_id}` - List resumes for job (with filters)
- `PATCH /api/resumes/{id}/bucket` - Update bucket
- `POST /api/resumes/{id}/send-screening-form` - Send screening form email
- `PATCH /api/resumes/{id}/email-status` - Update email status

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PyPDF2, Google Gemini API
- **Frontend**: Next.js 24.12.0, React 18, TypeScript
- **Database**: SQLite
- **AI**: Google Gemini (gemini-pro)

## License

This project is built for hackathon/demo purposes.

## Support

For issues or questions, refer to the codebase or API documentation at `/docs` endpoint.
