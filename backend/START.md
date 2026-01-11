# How to Run the Backend

## Prerequisites
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set the GEMINI_API_KEY environment variable:
   ```powershell
   # PowerShell:
   $env:GEMINI_API_KEY="your-api-key-here"
   
   # Or create a .env file in the backend directory:
   # GEMINI_API_KEY=your-api-key-here
   ```

## Running the Backend

### Option 1: Using uvicorn directly
```bash
cd backend
uvicorn app.main:app --reload
```

### Option 2: Using the run script
```bash
cd backend
python run.py
```

The server will start on `http://localhost:8000`

API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
