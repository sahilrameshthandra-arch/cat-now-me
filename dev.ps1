<# 
.SYNOPSIS
    cat-now-me Development Helper Script for PowerShell

.DESCRIPTION
    Provides common development commands for the cat-now-me monorepo.

.EXAMPLE
    .\dev.ps1 install
    .\dev.ps1 up
    .\dev.ps1 dev
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('install', 'up', 'down', 'logs', 'dev', 'dev-web', 'dev-api', 'build', 'test', 'lint', 'typecheck', 'db-migrate', 'pull-models', 'clean', 'help')]
    [string]$Command = 'help'
)

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VENV = Join-Path $ROOT "apps\api\venv"

function Show-Help {
    Write-Host "cat-now-me Development Helper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\dev.ps1 <command>"
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  install       - Install all dependencies"
    Write-Host "  up            - Start infrastructure (Docker)"
    Write-Host "  down          - Stop infrastructure"
    Write-Host "  logs          - View infrastructure logs"
    Write-Host "  dev           - Start both web and API dev servers"
    Write-Host "  dev-web       - Start only Next.js dev server"
    Write-Host "  dev-api       - Start only FastAPI dev server"
    Write-Host "  build         - Build all packages"
    Write-Host "  test          - Run all tests"
    Write-Host "  lint          - Lint all packages"
    Write-Host "  typecheck     - Type check all packages"
    Write-Host "  db-migrate    - Run database migrations"
    Write-Host "  pull-models   - Pull Ollama models"
    Write-Host "  clean         - Clean build artifacts"
    Write-Host "  help          - Show this help"
}

switch ($Command) {
    'install' {
        Write-Host "Installing dependencies..." -ForegroundColor Green
        npm ci
        Set-Location "$ROOT\apps\web" ; npm ci
        Set-Location "$ROOT\apps\api" ; if (-not (Test-Path $VENV)) { python -m venv venv }
        Set-Location "$ROOT\apps\api" ; & "$VENV\Scripts\python.exe" -m pip install --upgrade pip ; & "$VENV\Scripts\pip.exe" install -r requirements.txt
        Set-Location "$ROOT\packages\shared" ; npm ci
        Write-Host "Done!" -ForegroundColor Green
    }
    'up' {
        Write-Host "Starting infrastructure..." -ForegroundColor Green
        docker-compose up -d
        Write-Host ""
        Write-Host "Services starting..." -ForegroundColor Yellow
        Write-Host "  PostgreSQL:  localhost:5432"
        Write-Host "  Redis:       localhost:6379"
        Write-Host "  ChromaDB:    localhost:8001"
        Write-Host "  Ollama:      localhost:11434"
        Write-Host "  n8n:         localhost:5678 (admin/changeme)"
    }
    'down' {
        docker-compose down
    }
    'logs' {
        docker-compose logs -f
    }
    'dev' {
        Write-Host "Starting development servers..." -ForegroundColor Green
        Write-Host "Web:  http://localhost:3000"
        Write-Host "API:  http://localhost:8000"
        Write-Host "Docs: http://localhost:8000/docs"
        Write-Host ""
        Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
        
        # Start web in background job
        $webJob = Start-Job -ScriptBlock {
            param($root)
            Set-Location "$root\apps\web"
            npm run dev
        } -ArgumentList $ROOT
        
        # Start API in background job
        $apiJob = Start-Job -ScriptBlock {
            param($root, $venv)
            Set-Location "$root\apps\api"
            & "$venv\Scripts\Activate.ps1"
            uvicorn app.main:app --reload
        } -ArgumentList $ROOT, $VENV
        
        Write-Host "Servers started in background jobs. Use Ctrl+C to stop." -ForegroundColor Yellow
        Write-Host "Web Job ID: $($webJob.Id)"
        Write-Host "API Job ID: $($apiJob.Id)"
    }
    'dev-web' {
        Set-Location "$ROOT\apps\web"
        npm run dev
    }
    'dev-api' {
        Set-Location "$ROOT\apps\api"
        & "$VENV\Scripts\Activate.ps1"
        uvicorn app.main:app --reload
    }
    'build' {
        npm run build
    }
    'test' {
        Write-Host "Running tests..." -ForegroundColor Green
        Set-Location "$ROOT\apps\web" ; npm test --if-present
        Set-Location "$ROOT\apps\api" ; & "$VENV\Scripts\Activate.ps1" ; pytest -v --tb=short
        Set-Location "$ROOT\packages\shared" ; npm test --if-present
    }
    'lint' {
        Write-Host "Linting..." -ForegroundColor Green
        npm run lint
        Set-Location "$ROOT\apps\api" ; & "$VENV\Scripts\Activate.ps1" ; ruff check app ; black --check app
        Set-Location "$ROOT\packages\shared" ; npm run lint
    }
    'typecheck' {
        Write-Host "Type checking..." -ForegroundColor Green
        npm run typecheck
        Set-Location "$ROOT\apps\api" ; & "$VENV\Scripts\Activate.ps1" ; mypy app --ignore-missing-imports
    }
    'db-migrate' {
        Set-Location "$ROOT\apps\api" ; & "$VENV\Scripts\Activate.ps1" ; alembic upgrade head
    }
    'pull-models' {
        Write-Host "Pulling Ollama models..." -ForegroundColor Green
        ollama pull codellama:13b-instruct
        ollama pull deepseek-coder:6.7b
        ollama pull llama3.1:8b
        ollama pull nomic-embed-text
        ollama pull phi3:mini
    }
    'clean' {
        Write-Host "Cleaning..." -ForegroundColor Yellow
        $dirs = @(
            "node_modules",
            "$ROOT\apps\web\node_modules",
            "$ROOT\apps\web\.next",
            "$ROOT\apps\api\venv",
            "$ROOT\apps\api\__pycache__",
            "$ROOT\apps\api\.pytest_cache",
            "$ROOT\apps\api\.mypy_cache",
            "$ROOT\apps\api\.ruff_cache",
            "$ROOT\packages\shared\node_modules",
            "$ROOT\.turbo"
        )
        foreach ($dir in $dirs) {
            if (Test-Path $dir) {
                Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
                Write-Host "Removed: $dir"
            }
        }
        Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Recurse -Directory -Filter "*.egg-info" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Done!" -ForegroundColor Green
    }
    'help' {
        Show-Help
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}