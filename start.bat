@echo off
echo Starting Skills Chat...

:: 启动后端
start "FastAPI Backend" cmd /k "cd backend && uvicorn main:app --reload --port 8000"

:: 等待后端启动
timeout /t 2 /nobreak > nul

:: 启动前端
start "Vue3 Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit...
pause > nul
