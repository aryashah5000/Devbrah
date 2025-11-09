@echo off
REM Startup script for devbrah Frontend (Windows)

echo 🚀 Starting devbrah Frontend...
echo.

REM Install dependencies if needed
if not exist node_modules (
    echo 📦 Installing dependencies...
    call npm install
)

echo ✅ Starting Vite dev server...
echo 📍 Frontend will be available at http://localhost:5173
echo.

call npm run dev

pause



