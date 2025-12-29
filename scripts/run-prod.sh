#!/bin/bash
# Production run script for Literature Search Application
# Uses Gunicorn for the backend and serves static frontend files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}Starting Literature Search Application (Production)${NC}"
echo "======================================================="

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root is not recommended${NC}"
fi

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create a .env file from .env.example"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)

# Set production defaults
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=${LOG_LEVEL:-WARNING}

# Create necessary directories
echo "Creating directories..."
mkdir -p "$PROJECT_DIR/database"
mkdir -p "$PROJECT_DIR/papers"
mkdir -p "$PROJECT_DIR/cache"
mkdir -p "$PROJECT_DIR/output"
mkdir -p "$PROJECT_DIR/logs"

# Number of workers (2 * CPU cores + 1 is a good default)
WORKERS=${WORKERS:-$(( $(nproc) * 2 + 1 ))}
echo "Using $WORKERS Gunicorn workers"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Activate virtual environment
if [ -d "$PROJECT_DIR/.venv" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
else
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please run ./scripts/run-dev.sh --install first"
    exit 1
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}Installing Gunicorn...${NC}"
    pip install gunicorn
fi

# Build frontend for production
if [ ! -d "$PROJECT_DIR/frontend/dist" ] || [ "$1" == "--build" ]; then
    echo -e "\n${GREEN}Building frontend for production...${NC}"
    cd "$PROJECT_DIR/frontend"
    npm run build
    cd "$PROJECT_DIR"
fi

echo -e "\n${GREEN}Starting Gunicorn backend server...${NC}"
cd "$PROJECT_DIR"

# Start Gunicorn with production settings
gunicorn backend.main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile "$PROJECT_DIR/logs/access.log" \
    --error-logfile "$PROJECT_DIR/logs/error.log" \
    --capture-output \
    --log-level warning \
    --pid "$PROJECT_DIR/logs/gunicorn.pid" \
    --daemon

BACKEND_PID=$(cat "$PROJECT_DIR/logs/gunicorn.pid")

# Wait for backend to be ready
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend started successfully! (PID: $BACKEND_PID)${NC}"
        break
    fi
    sleep 1
done

echo -e "\n${GREEN}=======================================================${NC}"
echo -e "${GREEN}Application is running in production mode!${NC}"
echo -e "Backend:  http://localhost:8000"
echo -e "API Docs: http://localhost:8000/docs"
echo -e "Frontend: Serve ./frontend/dist with nginx or similar"
echo -e ""
echo -e "Logs:"
echo -e "  Access: $PROJECT_DIR/logs/access.log"
echo -e "  Error:  $PROJECT_DIR/logs/error.log"
echo -e "${GREEN}=======================================================${NC}"
echo -e ""
echo -e "To stop: kill \$(cat $PROJECT_DIR/logs/gunicorn.pid)"
