@echo off
REM Startup script for devbrah Backend (Windows)

echo 🚀 Starting devbrah Backend...
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo 📝 Please update .env with your Azure OpenAI credentials
    echo.
)

REM Create virtual environment if needed
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo ✅ Starting FastAPI server...
echo 📍 API will be available at http://localhost:8000
echo 📚 API docs at http://localhost:8000/docs
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause



