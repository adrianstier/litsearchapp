#!/bin/bash
# Docker run script for Literature Search Application
# Builds and runs the application using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default to development mode
MODE=${1:-dev}

echo -e "${GREEN}Literature Search Application - Docker${NC}"
echo "======================================================="

cd "$PROJECT_DIR"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Determine compose command (docker-compose vs docker compose)
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

case "$MODE" in
    dev)
        echo -e "${GREEN}Starting in development mode...${NC}"
        $COMPOSE_CMD up --build
        ;;
    prod)
        echo -e "${GREEN}Starting in production mode...${NC}"
        $COMPOSE_CMD -f docker-compose.prod.yml up --build -d
        echo -e "\n${GREEN}Application started in background${NC}"
        echo "Run '$COMPOSE_CMD -f docker-compose.prod.yml logs -f' to view logs"
        echo "Run '$COMPOSE_CMD -f docker-compose.prod.yml down' to stop"
        ;;
    build)
        echo -e "${GREEN}Building Docker images...${NC}"
        $COMPOSE_CMD build
        ;;
    stop)
        echo -e "${YELLOW}Stopping containers...${NC}"
        $COMPOSE_CMD down
        $COMPOSE_CMD -f docker-compose.prod.yml down 2>/dev/null || true
        echo -e "${GREEN}Containers stopped${NC}"
        ;;
    logs)
        $COMPOSE_CMD logs -f
        ;;
    status)
        echo -e "${GREEN}Container status:${NC}"
        docker ps --filter "name=litsearch"
        ;;
    *)
        echo "Usage: $0 {dev|prod|build|stop|logs|status}"
        echo ""
        echo "Commands:"
        echo "  dev    - Run in development mode (foreground)"
        echo "  prod   - Run in production mode (background)"
        echo "  build  - Build Docker images only"
        echo "  stop   - Stop all containers"
        echo "  logs   - View container logs"
        echo "  status - Show container status"
        exit 1
        ;;
esac
