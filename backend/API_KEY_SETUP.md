# How to Set Up Gemini API Key

## Option 1: Using .env File (Recommended)

1. **Create a `.env` file in the `backend/` directory:**
   ```bash
   cd backend
   ```

2. **Copy the example file:**
   ```bash
   copy .env.example .env
   ```

3. **Edit the `.env` file and add your API key:**
   ```
   GEMINI_API_KEY=your-actual-api-key-here
   ```

4. **The `.env` file is already in `.gitignore`, so it won't be committed to git.**

5. **The application will automatically load the `.env` file when you start it.**

## Option 2: Using Environment Variable (Temporary - Current Session Only)

### PowerShell:
```powershell
$env:GEMINI_API_KEY="your-actual-api-key-here"
```

### Command Prompt (cmd):
```cmd
set GEMINI_API_KEY=your-actual-api-key-here
```

### Linux/Mac:
```bash
export GEMINI_API_KEY="your-actual-api-key-here"
```

**Note:** This method only works for the current terminal session. If you close the terminal, you'll need to set it again.

## Option 3: Set System Environment Variable (Permanent)

### Windows:
1. Search for "Environment Variables" in Start Menu
2. Click "Edit the system environment variables"
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Variable name: `GEMINI_API_KEY`
6. Variable value: `your-actual-api-key-here`
7. Click OK and restart your terminal

## Get Your Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

## Verify It's Working

After setting the API key, start your backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

If the key is correctly set, the server will start without errors. You can test by uploading a resume - if the AI analysis works, your key is configured correctly.
