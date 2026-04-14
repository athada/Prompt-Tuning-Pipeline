#!/bin/bash

# Development mode startup script
# Starts only infrastructure (MongoDB, Temporal) in Docker
# API and UI run locally on the host

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

# Check if Ollama is installed
check_ollama() {
    print_status "Checking for Ollama installation..."
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama is not installed!"
        echo "Please install Ollama from: https://ollama.com"
        exit 1
    fi
    print_success "Ollama is installed"
}

# Start Ollama service
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

# Pull required model
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

# Start Docker infrastructure only
start_docker_infrastructure() {
    print_status "Starting Docker infrastructure (MongoDB + Temporal)..."
    compose -f docker-compose.dev.yml up -d
    print_success "Docker infrastructure started"
}

# Wait for infrastructure services
wait_for_infrastructure() {
    print_status "Waiting for infrastructure services to be healthy..."
    
    # Wait for MongoDB
    echo -n "Waiting for MongoDB"
    for i in {1..30}; do
        if compose -f docker-compose.dev.yml ps mongodb | grep -q "healthy"; then
            echo ""
            print_success "MongoDB is healthy"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Wait for Temporal
    echo -n "Waiting for Temporal"
    for i in {1..30}; do
        if compose -f docker-compose.dev.yml ps temporal | grep -q "healthy"; then
            echo ""
            print_success "Temporal is healthy"
            break
        fi
        echo -n "."
        sleep 2
    done
}

# Check Python environment
check_python_env() {
    print_status "Checking Python environment..."
    
    if [ ! -d "api-worker/venv" ]; then
        print_warning "Python virtual environment not found. Creating..."
        cd api-worker
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd "$REPO_ROOT"
        print_success "Python virtual environment created"
    else
        print_success "Python virtual environment exists"
    fi
}

# Check Node environment
check_node_env() {
    print_status "Checking Node.js environment..."
    
    if [ ! -d "ui/node_modules" ]; then
        print_warning "Node modules not found. Installing..."
        cd ui
        npm install
        cd "$REPO_ROOT"
        print_success "Node modules installed"
    else
        print_success "Node modules exist"
    fi
}

# Seed database
seed_database() {
    print_status "Seeding database with base prompts..."
    cd api-worker
    source venv/bin/activate
    python seed_db.py
    cd "$REPO_ROOT"
    print_success "Database seeded"
}

# Main execution
main() {
    echo "================================================"
    echo "Prompt Tuning Pipeline - Development Mode Setup"
    echo "================================================"
    echo ""

    compose_init || exit 1

    # Step 1: Check Ollama
    check_ollama
    
    # Step 2: Start Ollama
    start_ollama
    
    # Step 3: Pull required model
    pull_model "gemma2"
    
    # Step 4: Start Docker infrastructure only
    start_docker_infrastructure
    
    # Step 5: Wait for services
    wait_for_infrastructure
    
    # Step 6: Check Python environment
    check_python_env
    
    # Step 7: Check Node environment
    check_node_env
    
    # Step 8: Seed database
    sleep 3
    seed_database
    
    echo ""
    echo "================================================"
    print_success "Development Environment Ready!"
    echo "================================================"
    echo ""
    echo "Infrastructure Status:"
    echo "  ✓ MongoDB:       localhost:27017"
    echo "  ✓ Temporal:      localhost:7233"
    echo "  ✓ Temporal UI:   http://localhost:8088"
    echo "  ✓ Ollama:        http://localhost:11434"
    echo ""
    echo "To start the application in DEV mode:"
    echo ""
    echo "  Terminal 1 - Start API/Worker:"
    echo "    cd api-worker"
    echo "    source venv/bin/activate"
    echo "    cp .env.dev .env"
    echo "    python main.py"
    echo ""
    echo "  Terminal 2 - Start UI:"
    echo "    cd ui"
    echo "    cp .env.dev .env.local"
    echo "    npm run dev"
    echo ""
    echo "Then access:"
    echo "  - Frontend: http://localhost:3000 (or Vite's port)"
    echo "  - API:      http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
    echo "To stop infrastructure:"
    echo "  ./scripts/shutdown-dev.sh"
    echo ""
}

main
