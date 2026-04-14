#!/bin/bash

# Shutdown production/deploy mode

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
# shellcheck source=lib/compose.sh
source "$SCRIPT_DIR/lib/compose.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo "================================================"
echo "Prompt Tuning Pipeline - Production Shutdown"
echo "================================================"
echo ""

# Stop Docker containers
print_status "Stopping all Docker containers..."
compose -f docker-compose.prod.yml down
print_success "Docker containers stopped"

# Optionally stop Ollama
read -p "Do you want to stop Ollama service? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Stopping Ollama service..."
    pkill -x "ollama" || true
    print_success "Ollama service stopped"
fi

echo ""
print_success "Production shutdown complete!"
