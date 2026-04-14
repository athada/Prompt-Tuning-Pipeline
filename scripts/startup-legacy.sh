#!/bin/bash

# Startup script for Prompt Tuning Pipeline (legacy: all services via docker-compose.legacy.yml)
# This script manages the entire system including the local Ollama instance

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=lib/compose.sh
source "$SCRIPT_DIR/lib/compose.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_ollama() {
    print_status "Checking for Ollama installation..."
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama is not installed!"
        echo "Please install Ollama from: https://ollama.com"
        exit 1
    fi
    print_success "Ollama is installed"
}

start_ollama() {
    print_status "Starting Ollama service..."
    
    if pgrep -x "ollama" > /dev/null; then
        print_warning "Ollama is already running"
    else
        ollama serve > /dev/null 2>&1 &
        sleep 3
        print_success "Ollama service started"
    fi
}

pull_model() {
    MODEL_NAME=${1:-gemma2}
    print_status "Checking for model: $MODEL_NAME"
    
    if ollama list | grep -q "$MODEL_NAME"; then
        print_success "Model $MODEL_NAME is already available"
    else
        print_status "Pulling model $MODEL_NAME (this may take a while)..."
        ollama pull "$MODEL_NAME"
        print_success "Model $MODEL_NAME pulled successfully"
    fi
}

start_docker() {
    print_status "Starting Docker containers..."
    compose -f docker-compose.legacy.yml up -d --build
    print_success "Docker containers started"
}

wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    echo -n "Waiting for API service"
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            echo ""
            print_success "API service is healthy"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    echo -n "Waiting for UI service"
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo ""
            print_success "UI service is healthy"
            break
        fi
        echo -n "."
        sleep 2
    done
}

seed_database() {
    print_status "Seeding database with initial prompts..."
    compose -f docker-compose.legacy.yml exec -T api-worker python seed_db.py
    print_success "Database seeded"
}

main() {
    echo "================================"
    echo "Prompt Tuning Pipeline - Startup"
    echo "================================"
    echo ""

    compose_init || exit 1

    check_ollama
    start_ollama
    pull_model "gemma2"
    start_docker
    wait_for_services
    sleep 5
    seed_database
    
    echo ""
    echo "================================"
    print_success "Prompt Tuning Pipeline is ready!"
    echo "================================"
    echo ""
    echo "Service URLs:"
    echo "  - Frontend UI:      http://localhost:3000"
    echo "  - API Server:       http://localhost:8000"
    echo "  - API Docs:         http://localhost:8000/docs"
    echo "  - Temporal UI:      http://localhost:8088"
    echo "  - Ollama:           http://localhost:11434"
    echo ""
    echo "To view logs: ./scripts/dcompose -f docker-compose.legacy.yml logs -f"
    echo "To stop:      ./scripts/shutdown-legacy.sh"
    echo ""
}

main
