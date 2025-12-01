.PHONY: help dev build up down test clean db-init db-upgrade load-data

help:
	@echo "Available commands:"
	@echo "  make dev          - Start development environment"
	@echo "  make build        - Build Docker images"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make test         - Run tests"
	@echo "  make db-init      - Initialize database"
	@echo "  make db-upgrade   - Run database migrations"
	@echo "  make load-data    - Load sample data"
	@echo "  make clean        - Clean up containers and volumes"

dev: build up
	@echo "Development environment started. Frontend: http://localhost:3000, Backend: http://localhost:5000"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@make db-upgrade
	@echo "Services are ready!"

down:
	docker-compose down

test:
	cd backend && pytest --cov=app --cov-report=html --cov-report=term

db-init:
	cd backend && flask db init

db-upgrade:
	cd backend && flask db upgrade || (flask db init && flask db migrate -m "Initial migration" && flask db upgrade)

load-data:
	@echo "Use: docker-compose exec backend python scripts/load_documents_from_folder.py --folder /documents"

clean:
	docker-compose down -v
	docker system prune -f
