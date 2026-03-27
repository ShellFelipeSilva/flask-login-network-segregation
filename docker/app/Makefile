.PHONY: help up down logs build test prod dev tools

help:
	@echo "Available commands:"
	@echo "  make dev     - Start development environment"
	@echo "  make prod    - Start production environment"
	@echo "  make tools   - Start optional tools (pgAdmin, Redis, MailHog)"
	@echo "  make up      - Start base services"
	@echo "  make down    - Stop all services"
	@echo "  make logs    - View logs"
	@echo "  make build   - Rebuild images"

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

tools:
	docker-compose -f docker-compose.yml -f docker-compose.tools.yml --profile tools up -d

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose build

init-db:
	docker-compose exec web flask init-db