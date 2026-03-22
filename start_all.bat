@echo off
chcp 65001 >nul
echo ========================================
echo  啟動 合約審閱系統 所有服務
echo ========================================
echo.

:: --- 1. Docker Desktop ---
echo [1/5] 啟動 Docker Desktop...
set DOCKER_PATH=C:\Program Files\Docker\Docker\Docker Desktop.exe
if exist "%DOCKER_PATH%" (
    start "" "%DOCKER_PATH%"
) else (
    echo [警告] 找不到 Docker Desktop，請手動啟動
)

echo     等待 Docker 引擎就緒（約 20 秒）...
timeout /t 20 /nobreak >nul

:: 確認 Docker 是否已就緒
:wait_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo     Docker 尚未就緒，再等 5 秒...
    timeout /t 5 /nobreak >nul
    goto wait_docker
)
echo     [OK] Docker 已就緒
echo.

:: --- 2. Dify ---
echo [2/5] 啟動 Dify（Docker Compose）...
cd /d C:\dify\dify\docker
start "Dify" cmd /k "docker compose up 2>&1"
echo     [OK] Dify 啟動中（http://127.0.0.1:3001）
echo.

:: --- 3. n8n ---
echo [3/5] 啟動 n8n...
start "n8n" cmd /k "n8n start"
echo     [OK] n8n 啟動中（http://127.0.0.1:5678）
echo.

:: --- 4. Ollama ---
echo [4/5] 啟動 Ollama...
start "Ollama" cmd /k "ollama serve"
echo     [OK] Ollama 啟動中（http://127.0.0.1:11434）
echo.

:: --- 5. FastAPI 後端 ---
echo [5/6] 啟動 FastAPI 後端...
start "Backend" cmd /k "cd /d C:\contract-review-system\backend && python main.py"
echo     [OK] 後端啟動中（http://127.0.0.1:8000）
echo.

:: --- 6. Vue 前端 ---
echo [6/6] 啟動 Vue 前端...
start "Frontend" cmd /k "cd /d C:\contract-review-system\frontend && set NODE_ENV=development && npm run dev"
echo     [OK] 前端啟動中（http://127.0.0.1:5173）
echo.

echo ========================================
echo  全部服務已送出啟動指令
echo  請等待約 30 秒後再開啟瀏覽器
echo.
echo  Dify     -> http://127.0.0.1:3001
echo  n8n      -> http://127.0.0.1:5678
echo  Ollama   -> http://127.0.0.1:11434
echo  Backend  -> http://127.0.0.1:8000/docs
echo  Frontend -> http://127.0.0.1:5173
echo ========================================
pause
