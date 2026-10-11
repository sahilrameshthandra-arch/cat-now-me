# cat-now-me Makefile
# Common development commands

.PHONY: help install dev build test lint typecheck clean docker-up docker-down docker-logs db-migrate db-reset

# Default target
help:
	@echo "cat-now-me Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install all dependencies"
	@echo "  make docker-up        Start infrastructure (PostgreSQL, Redis, ChromaDB, Ollama, n8n)"
	@echo "  make docker-down      Stop infrastructure"
	@echo "  make docker-logs      View infrastructure logs"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start both web and API dev servers"
	@echo "  make dev-web          Start only Next.js dev server"
	@echo "  make dev-api          Start only FastAPI dev server"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate       Run database migrations"
	@echo "  make db-reset         Reset database (WARNING: destroys data)"
	@echo ""
	@echo "Quality:"
	@echo "  make lint             Lint all packages"
	@echo "  make typecheck        TypeScript/Python type checking"
	@echo "  make format           Format code (Black + Prettier)"
	@echo "  make test             Run all tests"
	@echo ""
	@echo "Build:"
	@echo "  make build            Build all packages"
	@echo "  make docker-build     Build Docker images"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove build artifacts and caches"

# ============================================
# Setup
# ============================================
install:
	npm ci
	cd apps/web && npm ci
	cd apps/api && python -m venv venv && . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	cd packages/shared && npm ci

docker-up:
	docker-compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@echo "Infrastructure started!"
	@echo "  PostgreSQL:  localhost:5432"
	@echo "  Redis:       localhost:6379"
	@echo "  ChromaDB:    localhost:8001"
	@echo "  Ollama:      localhost:11434"
	@echo "  n8n:         localhost:5678 (admin/changeme)"

docker-down:
	docker-compose down

docker-down-v:
	docker-compose down -v

docker-logs:
	docker-compose logs -f

docker-ps:
	docker-compose ps

# ============================================
# Development
# ============================================
dev:
	@echo "Starting development servers..."
	@echo "Web:  http://localhost:3000"
	@echo "API:  http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	npm run dev

dev-web:
	cd apps/web && npm run dev

dev-api:
	cd apps/api && . venv/bin/activate && uvicorn app.main:app --reload

# ============================================
# Database
# ============================================
db-migrate:
	cd apps/api && . venv/bin/activate && alembic upgrade head

db-revision:
	cd apps/api && . venv/bin/activate && alembic revision --autogenerate -m "$(msg)"

db-reset:
	@echo "WARNING: This will destroy all data!"
	@read -p "Are you sure? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose exec postgres psql -U postgres -c "DROP DATABASE cat_now_me; CREATE DATABASE cat_now_me;"
	cd apps/api && . venv/bin/activate && alembic upgrade head

# ============================================
# Quality
# ============================================
lint:
	npm run lint
	cd apps/api && . venv/bin/activate && ruff check app
	cd apps/api && . venv/bin/activate && black --check app

format:
	cd apps/web && npm run format 2>/dev/null || npx prettier --write .
	cd apps/api && . venv/bin/activate && black app
	cd apps/api && . venv/bin/activate && ruff check --fix app

typecheck:
	npm run typecheck
	cd apps/api && . venv/bin/activate && mypy app --ignore-missing-imports

test:
	cd apps/web && npm test --if-present
	cd apps/api && . venv/bin/activate && pytest -v --tb=short
	cd packages/shared && npm test --if-present

# ============================================
# Build
# ============================================
build:
	npm run build

docker-build:
	docker-compose build

docker-build-api:
	docker-compose build api

docker-build-web:
	docker-compose build web

# ============================================
# Cleanup
# ============================================
clean:
	rm -rf node_modules
	rm -rf apps/web/node_modules apps/web/.next
	rm -rf apps/api/venv apps/api/__pycache__ apps/api/.pytest_cache apps/api/.mypy_cache apps/api/.ruff_cache
	rm -rf packages/shared/node_modules
	rm -rf .turbo
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

# ============================================
# Models
# ============================================
pull-models:
	ollama pull codellama:13b-instruct
	ollama pull deepseek-coder:6.7b
	ollama pull llama3.1:8b
	ollama pull nomic-embed-text
	ollama pull phi3:mini

list-models:
	ollama list