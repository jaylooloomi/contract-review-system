@echo off
echo ========================================
echo  Start Contract Review System
echo ========================================
echo.

:: --- 1. Docker Desktop ---
echo [1/6] Starting Docker Desktop...
set DOCKER_PATH=C:\Program Files\Docker\Docker\Docker Desktop.exe
if exist "%DOCKER_PATH%" (
    start "" "%DOCKER_PATH%"
) else (
    echo [WARN] Docker Desktop not found, please start manually
)

echo     Waiting for Docker engine (20 sec)...
timeout /t 20 /nobreak >nul

:wait_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo     Docker not ready, waiting 5 more sec...
    timeout /t 5 /nobreak >nul
    goto wait_docker
)
echo     [OK] Docker ready
echo.

:: --- 1.5. pdf2htmlEX Image ---
echo [1.5/6] Checking pdf2htmlEX Docker image...
docker image inspect iapain/pdf2htmlex >nul 2>&1
if errorlevel 1 (
    echo     Image not found, pulling iapain/pdf2htmlex...
    docker pull iapain/pdf2htmlex
    if errorlevel 1 (
        echo     [ERROR] Failed to pull iapain/pdf2htmlex, PDF conversion will not work
    ) else (
        echo     [OK] iapain/pdf2htmlex pulled successfully
    )
) else (
    echo     [OK] iapain/pdf2htmlex image already exists
)
echo.

:: --- 2. Dify ---
echo [2/6] Starting Dify (Docker Compose)...
set DIFY_PATH=C:\dify\dify\docker
if exist "%DIFY_PATH%" (
    start "Dify" cmd /k "cd /d %DIFY_PATH% && docker compose up 2>&1"
    echo     [OK] Dify starting at http://127.0.0.1:3001
) else (
    echo     [WARN] Dify path not found: %DIFY_PATH%, skipping
)
echo.

:: --- 3. n8n ---
echo [3/6] Starting n8n...
start "n8n" cmd /k "n8n start"
echo     [OK] n8n starting at http://127.0.0.1:5678
echo.

:: --- 4. Ollama ---
echo [4/6] Starting Ollama...
start "Ollama" cmd /k "ollama serve"
echo     [OK] Ollama starting at http://127.0.0.1:11434
echo.

:: --- 5. FastAPI Backend ---
echo [5/6] Starting FastAPI Backend...
start "Backend" cmd /k "cd /d C:\contract-review-system\backend && python main.py"
echo     [OK] Backend starting at http://127.0.0.1:8000
echo.

:: --- 6. Vue Frontend ---
echo [6/6] Starting Vue Frontend...
start "Frontend" cmd /k "cd /d C:\contract-review-system\frontend && npm run dev"
echo     [OK] Frontend starting at http://127.0.0.1:5173
echo.

echo ========================================
echo  All services launched
echo  Wait ~30 sec then open browser
echo.
echo  Dify     -> http://127.0.0.1:3001
echo  n8n      -> http://127.0.0.1:5678
echo  Ollama   -> http://127.0.0.1:11434
echo  Backend  -> http://127.0.0.1:8000/docs
echo  Frontend -> http://127.0.0.1:5173
echo ========================================
pause
