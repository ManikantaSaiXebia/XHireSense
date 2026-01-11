from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database import init_db
from app.routers import jobs, resumes

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="XHireSense API",
    description="Explainable AI for Smarter Hiring Decisions",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(jobs.router)
app.include_router(resumes.router)

@app.get("/")
async def root():
    return {
        "message": "XHireSense API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
