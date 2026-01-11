# PROMPT_LOG

## 🟢 Prompt 01 — Initial project generation prompt

**Prompt Used**
You are an elite senior full-stack engineer, system architect, and AI engineer.



Your task is to BUILD a COMPLETE, WORKING, END-TO-END web application called **XHireSense**.



This is NOT a demo script.
This is NOT pseudocode.
This is NOT a partial implementation.



You must generate a REAL, RUNNABLE application with clean architecture, working APIs, and a usable UI.



========================
PROJECT IDENTITY
========================
Project Name: XHireSense
Tagline: Explainable AI for Smarter Hiring Decisions



Core Philosophy:
XHireSense is NOT a resume keyword matcher.
XHireSense IS an AI-powered hiring decision assistant.
Transparency, explainability, and recruiter trust are mandatory.



========================
TECH STACK (STRICT – DO NOT CHANGE)
========================
Backend:
- Python 3.10
- FastAPI
- SQLAlchemy ORM
- SQLite database (file-based)



Frontend:
- Next.js 24.12.0 (App Router)
- Fetch API (no deprecated patterns)



LLM:
- Google Gemini (used ONLY for resume matching)
- Must be isolated in a dedicated AI service layer



========================
FUNCTIONAL REQUIREMENTS
========================



1. JOB MANAGEMENT
- Landing page lists all jobs
- Ability to create a new job with:
  - Job title
  - Job description (markdown allowed)
- Clicking a job opens a Job Detail page



2. RESUME UPLOAD & PROCESSING
- Job Detail page allows:
  - Uploading multiple resumes
  - PDF files ONLY
- Backend must:
  - Extract text from PDF
  - Store extracted text
  - Associate resume with job



3. AI RESUME MATCHING (CRITICAL)
For EVERY uploaded resume:
- Call Google Gemini
- Compare resume text with job description
- Generate:
  - Match percentage (0–100)
  - Explainable AI output



ABSOLUTE OUTPUT CONTRACT:
Gemini MUST return ONLY VALID JSON in EXACTLY this format:



{
  "match_percentage": number,
  "matched_skills": string[],
  "missing_skills": string[],
  "bonus_skills": string[],
  "reasoning": string
}



NO markdown.
NO prose.
NO additional keys.
NO text outside JSON.



If output is malformed:
- Retry once
- If still invalid, fail safely and log error



4. SMART CANDIDATE BUCKETING (MANDATORY)
Automatically assign each resume to a bucket:



- STRONG_FIT → match >= 80
- POTENTIAL → match 60–79
- REJECT → match < 60



Rules:
- Bucket logic runs server-side
- Bucket is stored in DB
- Recruiter can manually override bucket



5. EXPLAINABLE AI UI (NON-NEGOTIABLE)
For EACH resume display:
- Match percentage
- Bucket label (color-coded)
- Matched skills (✔)
- Missing skills (⚠)
- Bonus skills (⭐)
- Short AI reasoning (2–3 lines)



Black-box scoring is FORBIDDEN.



6. SORTING & FILTERING
- Default sort: highest match first
- Filters:
  - By bucket
  - By minimum match percentage



7. AUTOMATED EMAIL ACTION
- Each resume card has “Send Screening Form”
- Sends an email containing:
  - Microsoft Form link
- Track email status:
  - NOT_SENT
  - SENT
  - RESPONSE_RECEIVED



8. JOB DASHBOARD
Per job, show:
- Total resumes
- Strong / Potential / Reject counts
- Average match percentage
- Pending screening responses



========================
DATABASE REQUIREMENTS (SQLITE)
========================
Use SQLAlchemy models.
NO raw SQL.



Required tables:
- Job
- Resume
- ResumeAnalysis
- EmailStatus



Data must persist across restarts.



========================
BACKEND ARCHITECTURE
========================
Use FastAPI with modular structure:



- app/main.py
- app/database.py
- app/models/
- app/routers/
- app/services/
  - ai_service.py (Gemini ONLY)
  - pdf_service.py
  - email_service.py



Rules:
- One DB session per request
- Defensive error handling
- Clear logging



========================
FRONTEND ARCHITECTURE
========================
Next.js App Router.



Pages:
- /jobs (job list + create)
- /jobs/[id] (job details, resumes, dashboard)



UI Rules:
- Resume cards
- Bucket tabs
- Clear visual hierarchy
- Recruiter-friendly layout



========================
AI SCORING RULES (VERY IMPORTANT)
========================
When prompting Gemini:
- Include full job description
- Include full resume text
- Include explicit scoring rubric:
  - Core skills = high weight
  - Nice-to-have skills = medium weight
  - Experience alignment matters
  - Missing critical skills must reduce score



Match percentage must feel:
- Conservative
- Realistic
- Explainable



========================
NON-FUNCTIONAL REQUIREMENTS
========================
- Deterministic behavior where possible
- Graceful failure on AI errors
- No hardcoded demo data
- Hackathon-ready but production-minded



========================
DELIVERABLES
========================
You MUST generate:
- Full FastAPI backend code
- Full Next.js frontend code
- SQLite schema via SQLAlchemy
- Gemini prompt template
- README explaining:
  - Architecture
  - AI flow
  - How to run locally



========================
FINAL INSTRUCTIONS
========================
Build the FULL SYSTEM end-to-end.
Do NOT skip features.
Do NOT simplify architecture.
Do NOT remove explainability or bucketing.
Assume this will be judged by senior engineers.



START BUILDING NOW.
 
**Change Made**

Initialized FastAPI backend with modular structure

Configured SQLite using SQLAlchemy

Bootstrapped Next.js frontend with App Router

**Impact / Result**

Established scalable foundation

Enabled parallel development

Generated Skeleton for application

## 🟢 Prompt 03 — Job Listing Page (Recruiter Entry Point)

**Prompt Used**

Implement a job listing page that serves as the primary recruiter entry point.
Fetch jobs from backend API, display them in a clean list, and allow navigation to individual job detail pages.

**Change Made**

Created job list API endpoint

Implemented frontend job listing page

Enabled job detail navigation

**Impact / Result**

Clear recruiter workflow starting point

Improved discoverability of job postings

## 🟢 Prompt 04 — Job Creation with Validation

**Prompt Used**

Add a job creation flow allowing recruiters to create a job with title and description.
Include frontend validation, backend persistence, and error handling to prevent invalid job entries.

**Change Made**

Job creation API implemented

Frontend form with validation rules

Job persisted in SQLite

**Impact / Result**

Recruiters can create jobs end-to-end

Reduced invalid or incomplete job data

## 🟢 Prompt 05 — Safe Job Deletion

**Prompt Used**

Implement job deletion functionality with user confirmation.
Ensure deletion does not silently corrupt related resume data and provides clear UI feedback.

**Change Made**

Job delete API

Confirmation modal in UI

Safe handling of related data

**Impact / Result**

Controlled job lifecycle

Reduced accidental deletions

## 🟢 Prompt 06 — Resume Upload (Single File)

**Prompt Used**

Enable resume upload functionality for a job.
Accept PDF files only, store metadata, and associate each resume with its job.

**Change Made**

Resume upload API

File validation and storage

Job–resume association

**Impact / Result**

Core resume ingestion workflow enabled

## 🟢 Prompt 07 — Resume Upload (Multiple Files)

**Prompt Used**

Extend resume upload to support selecting and uploading multiple PDF files in a single action.
Ensure backend processes files independently so one failure does not affect others.

**Change Made**

Multi-file upload support

Backend batch handling

**Impact / Result**

Faster recruiter workflows

Improved scalability

## 🟢 Prompt 08 — Resume Deletion & Cleanup

**Prompt Used**

Add resume deletion capability allowing recruiters to remove incorrectly uploaded resumes.
Ensure database and file system remain consistent.

**Change Made**

Resume delete API

UI delete action

DB cleanup

**Impact / Result**

Improved data hygiene

Error recovery without admin intervention

## 🟢 Prompt 09 — PDF Text Extraction Pipeline

**Prompt Used**

Implement a PDF parsing service to extract raw text from resumes.
Ensure extracted text is stored for downstream AI analysis and handle parsing errors gracefully.

**Change Made**

PDF parsing service added

Extracted text persisted

**Impact / Result**

Enabled AI-driven analysis

Removed manual preprocessing

## 🟢 Prompt 10 — Email Extraction from Resume Text

**Prompt Used**

Analyze extracted resume text to reliably identify candidate email addresses.
Handle multiple formats, edge cases, and store extracted email for communication workflows.

**Change Made**

Email extraction logic

Email persisted per resume

**Impact / Result**

Automated candidate contact

Reduced manual lookup

## 🟢 Prompt 11 — Candidate Card Component

**Prompt Used**

Design a candidate card UI component that encapsulates resume-related actions and metadata in a recruiter-friendly format.

**Change Made**

Candidate card UI introduced

Resume actions centralized

**Impact / Result**

Improved information clarity

Cleaner UI structure

## 🟢 Prompt 12 — Candidate Card UX Refinement

**Prompt Used**

Improve candidate card layout by optimizing spacing, typography, and action placement to reduce cognitive load for recruiters.

**Change Made**

Visual hierarchy improvements

Action grouping

**Impact / Result**

Faster candidate scanning

Reduced visual clutter

## 🟢 Prompt 13 — Email Sending Capability

**Prompt Used**

Add functionality to send emails to candidates directly from the system using extracted email addresses.
Ensure failures are detectable and logged.

**Change Made**

Email service integration

“Send Email” action

**Impact / Result**

Automated outreach

Centralized communication

## 🟢 Prompt 14 — Email Status Tracking

**Prompt Used**

Track email sending status per candidate and surface it clearly in the UI to prevent duplicate or missed communications.

**Change Made**

Email status field added

UI status indicators

**Impact / Result**

Improved communication visibility

Reduced duplicate emails

## 🟢 Prompt 15 — Confirmation Modal UX Improvement

**Prompt Used**

Improve confirmation dialogs for destructive actions by enhancing visual cues, button hierarchy, and clarity of intent.

**Change Made**

Modal styling updates

Clear primary/secondary actions

**Impact / Result**

Reduced accidental actions

More professional UX

## 🟢 Prompt 16 — UI Version 1 Polish

**Prompt Used**

Perform a UI polish pass to improve alignment, spacing, and consistency across pages without changing functionality.

**Change Made**

Minor UI refinements

Layout consistency improvements

**Impact / Result**

Demo-ready UI

Improved perceived quality

## 🟢 Prompt 17 — Bug Fixes & Stability Pass

**Prompt Used**

Identify and fix UI and API bugs discovered during usage without introducing breaking changes.

**Change Made**

UI bug fixes

API response corrections

**Impact / Result**

Improved stability

Reduced runtime errors

## 🟢 Prompt 18 — Secure API Key Management

**Prompt Used**

Refactor configuration to remove hardcoded API keys and load all secrets from environment variables.

**Change Made**

Environment-based configuration

Secrets removed from code

**Impact / Result**

Improved security posture

Production readiness

## 🟢 Prompt 19 — Branch Merge & Conflict Resolution

**Prompt Used**

Merge feature branches safely, resolve conflicts carefully, and validate all critical workflows post-merge.

**Change Made**

Branch merges completed

Conflicts resolved

**Impact / Result**

Stable main branch

Continued development enabled

## 🟢 Prompt 20 — Resume Upload Feedback UX

**Prompt Used**

Improve resume upload UX by adding success, failure, and validation feedback for each uploaded file.

**Change Made**

Upload status indicators

Clear error messaging

**Impact / Result**

Reduced user confusion

Faster issue resolution

## 🟢 Prompt 21 — Defensive PDF Error Handling

**Prompt Used**

Add safeguards to ensure corrupted or unsupported PDFs do not break batch uploads or crash the system.

**Change Made**

Try/catch around parsing

Per-file failure handling

**Impact / Result**

Increased robustness

Safer batch operations

## 🟢 Prompt 22 — Database Consistency Safeguards

**Prompt Used**

Ensure database consistency when resumes are uploaded or deleted by using transactional boundaries.

**Change Made**

Transaction-safe operations

Orphan prevention

**Impact / Result**

Improved data integrity

Reduced corruption risk

## 🟢 Prompt 23 — Backend Logging Improvements

**Prompt Used**

Introduce structured logging for critical backend operations including uploads, deletions, and email sends.

**Change Made**

Logging added across services

**Impact / Result**

Easier debugging

Better observability

## 🟢 Prompt 24 — Codebase Refactoring Pass

**Prompt Used**

Refactor code to improve readability, naming clarity, and maintainability without altering behavior.

**Change Made**

Removed dead code

Improved naming conventions

**Impact / Result**

Cleaner codebase

Easier onboarding

## 🟢 Prompt 25 — UI Consistency Enforcement

**Prompt Used**

Ensure consistent button styles, spacing, and visual language across all UI components.

**Change Made**

Standardized UI components

**Impact / Result**

Cohesive visual experience

Reduced visual friction

## 🟢 Prompt 26 — User-Facing Error Message Clarity

**Prompt Used**

Rewrite user-facing error messages to be clear, actionable, and non-technical.

**Change Made**

Improved error copy

Added contextual hints

**Impact / Result**

Better user understanding

Reduced frustration

## 🟢 Prompt 27 — Hackathon Demo Stability Review

**Prompt Used**

Review the entire application for demo readiness, focusing on stability, edge cases, and predictable behavior.

**Change Made**

Minor fixes

Validation of core flows

**Impact / Result**

Reliable demo experience

Reduced last-minute risk

## 🟢 Prompt 28 — Prompt Governance & Audit Trail

**Prompt Used**

Create and maintain a PROMPT_LOG documenting detailed AI prompts, corresponding changes, and measurable impact.

**Change Made**

Introduced and expanded PROMPT_LOG.md

**Impact / Result**

Clear AI governance trail

Strong signal of responsible AI usage
