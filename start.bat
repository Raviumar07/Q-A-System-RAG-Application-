@echo off
REM Quick start script for Q&A System (RAG Application)
echo 🚀 Starting Q&A System (RAG Application)
echo =====================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found. Please run setup.py first.
    echo Run: python setup.py
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Please configure your API credentials.
    echo Edit .env file with your Azure OpenAI details.
    pause
)

echo 🔧 Activating virtual environment...
call .venv\Scripts\activate

echo 📡 Starting backend API...
start "RAG Backend" cmd /k "cd src\backend\api && python main.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo 🌐 Starting frontend...
start "RAG Frontend" cmd /k "cd src\frontend && streamlit run app.py"

echo ✅ Both services are starting!
echo 🌐 Frontend: http://localhost:8501
echo 📡 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs

pause
