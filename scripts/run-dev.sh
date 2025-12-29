#!/bin/bash
# Development run script for Literature Search Application
# Runs both backend and frontend in development mode

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}Starting Literature Search Application (Development)${NC}"
echo "======================================================="

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Copying from .env.example${NC}"
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
fi

# Load environment variables
export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)

# Create necessary directories
echo "Creating directories..."
mkdir -p "$PROJECT_DIR/database"
mkdir -p "$PROJECT_DIR/papers"
mkdir -p "$PROJECT_DIR/cache"
mkdir -p "$PROJECT_DIR/output"
mkdir -p "$PROJECT_DIR/logs"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Check Node version
NODE_VERSION=$(node --version 2>&1)
echo "Node version: $NODE_VERSION"

# Install Python dependencies if needed
if [ ! -d "$PROJECT_DIR/.venv" ] || [ "$1" == "--install" ]; then
    echo -e "\n${GREEN}Setting up Python virtual environment...${NC}"
    python3 -m venv "$PROJECT_DIR/.venv"
    source "$PROJECT_DIR/.venv/bin/activate"
    pip install --upgrade pip
    pip install -e ".[dev,ai]"
    pip install fastapi uvicorn sqlalchemy python-multipart
else
    source "$PROJECT_DIR/.venv/bin/activate"
fi

# Install frontend dependencies if needed
if [ ! -d "$PROJECT_DIR/frontend/node_modules" ] || [ "$1" == "--install" ]; then
    echo -e "\n${GREEN}Installing frontend dependencies...${NC}"
    cd "$PROJECT_DIR/frontend"
    npm install --legacy-peer-deps
    cd "$PROJECT_DIR"
fi

echo -e "\n${GREEN}Starting backend server...${NC}"
cd "$PROJECT_DIR"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend started successfully!${NC}"
        break
    fi
    sleep 1
done

echo -e "\n${GREEN}Starting frontend server...${NC}"
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo -e "\n${GREEN}=======================================================${NC}"
echo -e "${GREEN}Application is running!${NC}"
echo -e "Backend:  http://localhost:8000"
echo -e "Frontend: http://localhost:5173"
echo -e "API Docs: http://localhost:8000/docs"
echo -e "${GREEN}=======================================================${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
