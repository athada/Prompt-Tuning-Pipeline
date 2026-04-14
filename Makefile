# Makefile for Prompt Tuning Pipeline

.PHONY: help dev-start dev-stop prod-start prod-stop start stop restart logs clean rebuild seed test status

help:
	@echo "Prompt Tuning Pipeline - Available Commands:"
	@echo ""
	@echo "Development Mode (API/UI run locally):"
	@echo "  make dev-start       - Start infrastructure only (MongoDB, Temporal)"
	@echo "  make dev-stop        - Stop development infrastructure"
	@echo "  make dev-api         - Run API/Worker locally (after dev-start)"
	@echo "  make dev-ui          - Run UI locally (after dev-start)"
	@echo ""
	@echo "Production/Deploy Mode (Everything in Docker):"
	@echo "  make prod-start      - Start all services in Docker"
	@echo "  make prod-stop       - Stop all Docker services"
	@echo "  make prod-logs       - View production logs"
	@echo "  make prod-rebuild    - Rebuild production containers"
	@echo ""
	@echo "Legacy Commands (uses old docker-compose.yml):"
	@echo "  make start           - Start all services (original)"
	@echo "  make stop            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - View logs from all services"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean           - Stop and remove all containers and volumes"
	@echo "  make seed-dev        - Seed database (dev mode)"
	@echo "  make seed-prod       - Seed database (prod mode)"
	@echo "  make status          - Show status of all services"
	@echo "  make health          - Check service health"
	@echo ""

# ============================================================================
# Development Mode Commands
# ============================================================================

dev-start:
	@echo "Starting Development Infrastructure..."
	@./startup-dev.sh

dev-stop:
	@echo "Stopping Development Infrastructure..."
	@./shutdown-dev.sh

dev-api:
	@echo "Starting API/Worker locally..."
	@echo "Make sure you've run 'make dev-start' first!"
	@cd api-worker && source venv/bin/activate && python main.py

dev-ui:
	@echo "Starting UI locally..."
	@echo "Make sure you've run 'make dev-start' first!"
	@cd ui && npm run dev

dev-setup:
	@echo "Setting up development environment..."
	@cd api-worker && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@cd ui && npm install
	@echo "Development environment ready!"

dev-logs:
	@docker-compose -f docker-compose.dev.yml logs -f

# ============================================================================
# Production/Deploy Mode Commands
# ============================================================================

prod-start:
	@echo "Starting Production Mode..."
	@./startup-prod.sh

prod-stop:
	@echo "Stopping Production Mode..."
	@./shutdown-prod.sh

prod-logs:
	@docker-compose -f docker-compose.prod.yml logs -f

prod-logs-api:
	@docker-compose -f docker-compose.prod.yml logs -f api-worker

prod-logs-ui:
	@docker-compose -f docker-compose.prod.yml logs -f ui

prod-rebuild:
	@echo "Rebuilding production containers..."
	@docker-compose -f docker-compose.prod.yml down
	@docker-compose -f docker-compose.prod.yml up -d --build
	@echo "Rebuild complete"

prod-shell-api:
	@docker-compose -f docker-compose.prod.yml exec api-worker /bin/bash

prod-status:
	@docker-compose -f docker-compose.prod.yml ps

# ============================================================================
# Legacy Commands (Original docker-compose.yml)
# ============================================================================

start:
	@echo "Starting Prompt Tuning Pipeline (legacy mode)..."
	@./startup.sh

stop:
	@echo "Stopping services..."
	@docker-compose down

restart: stop start

logs:
	@docker-compose logs -f

logs-api:
	@docker-compose logs -f api-worker

logs-ui:
	@docker-compose logs -f ui

logs-temporal:
	@docker-compose logs -f temporal

rebuild:
	@echo "Rebuilding services..."
	@docker-compose down
	@docker-compose up -d --build
	@echo "Rebuild complete"

# ============================================================================
# Utility Commands
# ============================================================================

clean:
	@echo "Cleaning up all containers and volumes..."
	@docker-compose down -v
	@docker-compose -f docker-compose.dev.yml down -v
	@docker-compose -f docker-compose.prod.yml down -v
	@echo "Cleanup complete"

seed-dev:
	@echo "Seeding database (dev mode)..."
	@cd api-worker && source venv/bin/activate && python seed_db.py

seed-prod:
	@echo "Seeding database (prod mode)..."
	@docker-compose -f docker-compose.prod.yml exec api-worker python seed_db.py

seed:
	@echo "Seeding database (legacy mode)..."
	@docker-compose exec api-worker python seed_db.py

status:
	@echo "=== Development Infrastructure ==="
	@docker-compose -f docker-compose.dev.yml ps
	@echo ""
	@echo "=== Production Services ==="
	@docker-compose -f docker-compose.prod.yml ps

shell-mongodb-dev:
	@docker-compose -f docker-compose.dev.yml exec mongodb mongosh

shell-mongodb-prod:
	@docker-compose -f docker-compose.prod.yml exec mongodb mongosh

health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/api/health | jq || echo "API not reachable"
	@echo ""
	@curl -s http://localhost:3000 > /dev/null && echo "UI: ✓ Healthy" || echo "UI: ✗ Unhealthy"
