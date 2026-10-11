@echo off
REM cat-now-me Development Helper Script for Windows
REM Usage: dev.bat [command]

setlocal enabledelayedexpansion

set ROOT=%~dp0
set VENV=%ROOT%apps\api\venv

if "%1"=="" (
    echo cat-now-me Development Helper
    echo.
    echo Usage: dev.bat ^<command^>
    echo.
    echo Commands:
    echo   install       - Install all dependencies
    echo   up            - Start infrastructure (Docker)
    echo   down          - Stop infrastructure
    echo   logs          - View infrastructure logs
    echo   dev           - Start both web and API dev servers
    echo   dev-web       - Start only Next.js dev server
    echo   dev-api       - Start only FastAPI dev server
    echo   build         - Build all packages
    echo   test          - Run all tests
    echo   lint          - Lint all packages
    echo   typecheck     - Type check all packages
    echo   db-migrate    - Run database migrations
    echo   pull-models   - Pull Ollama models
    echo   clean         - Clean build artifacts
    echo   help          - Show this help
    goto :eof
)

set COMMAND=%1

if "%COMMAND%"=="install" (
    echo Installing dependencies...
    npm ci
    cd /d "%ROOT%apps\web" && npm ci
    cd /d "%ROOT%apps\api" && if not exist "%VENV%" python -m venv venv
    cd /d "%ROOT%apps\api" && "%VENV%\Scripts\python.exe" -m pip install --upgrade pip && "%VENV%\Scripts\pip.exe" install -r requirements.txt
    cd /d "%ROOT%packages\shared" && npm ci
    echo Done!
    goto :eof
)

if "%COMMAND%"=="up" (
    echo Starting infrastructure...
    docker-compose up -d
    echo.
    echo Services starting...
    echo PostgreSQL:  localhost:5432
    echo Redis:       localhost:6379
    echo ChromaDB:    localhost:8001
    echo Ollama:      localhost:11434
    echo n8n:         localhost:5678 (admin/changeme)
    goto :eof
)

if "%COMMAND%"=="down" (
    docker-compose down
    goto :eof
)

if "%COMMAND%"=="logs" (
    docker-compose logs -f
    goto :eof
)

if "%COMMAND%"=="dev" (
    echo Starting development servers...
    echo Web:  http://localhost:3000
    echo API:  http://localhost:8000
    echo Docs: http://localhost:8000/docs
    echo.
    echo Press Ctrl+C to stop both servers
    start "Web Dev Server" cmd /k "cd /d "%ROOT%apps\web" && npm run dev"
    start "API Dev Server" cmd /k "cd /d "%ROOT%apps\api" && "%VENV%\Scripts\Activate.bat" && uvicorn app.main:app --reload"
    goto :eof
)

if "%COMMAND%"=="dev-web" (
    cd /d "%ROOT%apps\web" && npm run dev
    goto :eof
)

if "%COMMAND%"=="dev-api" (
    cd /d "%ROOT%apps\api" && "%VENV%\Scripts\Activate.bat" && uvicorn app.main:app --reload
    goto :eof
)

if "%COMMAND%"=="build" (
    npm run build
    goto :eof
)

if "%COMMAND%"=="test" (
    echo Running tests...
    cd /d "%ROOT%apps\web" && npm test --if-present
    cd /d "%ROOT%apps\api" && "%VENV%\Scripts\Activate.bat" && pytest -v --tb=short
    cd /d "%ROOT%packages\shared" && npm test --if-present
    goto :eof
)

if "%COMMAND%"=="lint" (
    echo Linting...
    npm run lint
    cd /d "%ROOT%apps\api" && "%VENV%\Scripts\Activate.bat" && ruff check app && black --check app
    cd /d "%ROOT%packages\shared" && npm run lint
    goto :eof
)

if "%COMMAND%"=="typecheck" (
    echo Type checking...
    npm run typecheck
    cd /d "%ROOT%apps\api" && "%VENV%\Scripts\Activate.bat" && mypy app --ignore-missing-imports
    goto :eof
)

if "%COMMAND%"=="db-migrate" (
    cd /d "%ROOT%apps\api" && "%VENV%\Scripts\Activate.bat" && alembic upgrade head
    goto :eof
)

if "%COMMAND%"=="pull-models" (
    echo Pulling Ollama models...
    ollama pull codellama:13b-instruct
    ollama pull deepseek-coder:6.7b
    ollama pull llama3.1:8b
    ollama pull nomic-embed-text
    ollama pull phi3:mini
    goto :eof
)

if "%COMMAND%"=="clean" (
    echo Cleaning...
    if exist node_modules rmdir /s /q node_modules
    if exist "%ROOT%apps\web\node_modules" rmdir /s /q "%ROOT%apps\web\node_modules"
    if exist "%ROOT%apps\web\.next" rmdir /s /q "%ROOT%apps\web\.next"
    if exist "%ROOT%apps\api\venv" rmdir /s /q "%ROOT%apps\api\venv"
    if exist "%ROOT%apps\api\__pycache__" rmdir /s /q "%ROOT%apps\api\__pycache__"
    if exist "%ROOT%apps\api\.pytest_cache" rmdir /s /q "%ROOT%apps\api\.pytest_cache"
    if exist "%ROOT%apps\api\.mypy_cache" rmdir /s /q "%ROOT%apps\api\.mypy_cache"
    if exist "%ROOT%apps\api\.ruff_cache" rmdir /s /q "%ROOT%apps\api\.ruff_cache"
    if exist "%ROOT%packages\shared\node_modules" rmdir /s /q "%ROOT%packages\shared\node_modules"
    if exist "%ROOT%\.turbo" rmdir /s /q "%ROOT%\.turbo"
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
    for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
    echo Done!
    goto :eof
)

if "%COMMAND%"=="help" (
    dev.bat
    goto :eof
)

echo Unknown command: %COMMAND%
echo Run "dev.bat help" for usage
exit /b 1