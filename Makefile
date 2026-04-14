# Makefile for Prompt Tuning Pipeline
# Compose: ./scripts/dcompose prefers `docker compose`, falls back to `docker-compose`

DC := ./scripts/dcompose

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
	@echo "Legacy Commands (uses docker-compose.legacy.yml):"
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
	@./scripts/startup-dev.sh

dev-stop:
	@echo "Stopping Development Infrastructure..."
	@./scripts/shutdown-dev.sh

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
	@$(DC) -f docker-compose.dev.yml logs -f

# ============================================================================
# Production/Deploy Mode Commands
# ============================================================================

prod-start:
	@echo "Starting Production Mode..."
	@./scripts/startup-prod.sh

prod-stop:
	@echo "Stopping Production Mode..."
	@./scripts/shutdown-prod.sh

prod-logs:
	@$(DC) -f docker-compose.prod.yml logs -f

prod-logs-api:
	@$(DC) -f docker-compose.prod.yml logs -f api-worker

prod-logs-ui:
	@$(DC) -f docker-compose.prod.yml logs -f ui

prod-rebuild:
	@echo "Rebuilding production containers..."
	@$(DC) -f docker-compose.prod.yml down
	@$(DC) -f docker-compose.prod.yml up -d --build
	@echo "Rebuild complete"

prod-shell-api:
	@$(DC) -f docker-compose.prod.yml exec api-worker /bin/bash

prod-status:
	@$(DC) -f docker-compose.prod.yml ps

# ============================================================================
# Legacy Commands (docker-compose.legacy.yml)
# ============================================================================

start:
	@echo "Starting Prompt Tuning Pipeline (legacy mode)..."
	@./scripts/startup-legacy.sh

stop:
	@echo "Stopping services..."
	@$(DC) -f docker-compose.legacy.yml down

restart: stop start

logs:
	@$(DC) -f docker-compose.legacy.yml logs -f

logs-api:
	@$(DC) -f docker-compose.legacy.yml logs -f api-worker

logs-ui:
	@$(DC) -f docker-compose.legacy.yml logs -f ui

logs-temporal:
	@$(DC) -f docker-compose.legacy.yml logs -f temporal

rebuild:
	@echo "Rebuilding services..."
	@$(DC) -f docker-compose.legacy.yml down
	@$(DC) -f docker-compose.legacy.yml up -d --build
	@echo "Rebuild complete"

# ============================================================================
# Utility Commands
# ============================================================================

clean:
	@echo "Cleaning up all containers and volumes..."
	@$(DC) -f docker-compose.legacy.yml down -v 2>/dev/null || true
	@$(DC) -f docker-compose.dev.yml down -v 2>/dev/null || true
	@$(DC) -f docker-compose.prod.yml down -v 2>/dev/null || true
	@echo "Cleanup complete"

seed-dev:
	@echo "Seeding database (dev mode)..."
	@cd api-worker && source venv/bin/activate && python seed_db.py

seed-prod:
	@echo "Seeding database (prod mode)..."
	@$(DC) -f docker-compose.prod.yml exec api-worker python seed_db.py

seed:
	@echo "Seeding database (legacy mode)..."
	@$(DC) -f docker-compose.legacy.yml exec api-worker python seed_db.py

status:
	@echo "=== Development Infrastructure ==="
	@$(DC) -f docker-compose.dev.yml ps
	@echo ""
	@echo "=== Production Services ==="
	@$(DC) -f docker-compose.prod.yml ps

shell-mongodb-dev:
	@$(DC) -f docker-compose.dev.yml exec mongodb mongosh

shell-mongodb-prod:
	@$(DC) -f docker-compose.prod.yml exec mongodb mongosh

health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/api/health | jq || echo "API not reachable"
	@echo ""
	@curl -s http://localhost:3000 > /dev/null && echo "UI: ✓ Healthy" || echo "UI: ✗ Unhealthy"
