#!/bin/bash

# Quick Start Script for Topic Discovery System
# This script will guide you through the build process step by step

set -e  # Exit on error

echo "=========================================="
echo "Topic Discovery System - Build Guide"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"
echo ""

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"
echo -e "${GREEN}✅ Docker Compose found: $(docker-compose --version)${NC}"
echo ""

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker.${NC}"
    echo "If you get permission denied, run: sudo usermod -aG docker \$USER && newgrp docker"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Step 2: Check environment files
echo -e "${YELLOW}Step 2: Checking environment configuration...${NC}"
echo ""

if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env not found. Creating from example...${NC}"
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✅ Created backend/.env${NC}"
        echo -e "${RED}⚠️  IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY!${NC}"
        echo ""
        read -p "Press Enter after you've added your OpenAI API key to backend/.env..."
    else
        echo -e "${RED}❌ backend/.env.example not found!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ backend/.env exists${NC}"
    
    # Check if API key is set
    if ! grep -q "OPENAI_API_KEY=sk-" backend/.env 2>/dev/null; then
        echo -e "${RED}⚠️  WARNING: OPENAI_API_KEY doesn't appear to be set in backend/.env${NC}"
        echo "Please edit backend/.env and add your OpenAI API key"
        read -p "Press Enter after you've added your OpenAI API key..."
    else
        echo -e "${GREEN}✅ OPENAI_API_KEY appears to be set${NC}"
    fi
fi

# Check root .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Root .env not found. Creating...${NC}"
    cat >> .env << 'EOF'

# Frontend Environment Variables
VITE_API_URL=http://backend:5000
VITE_ENV=development
EOF
    echo -e "${GREEN}✅ Created root .env${NC}"
else
    echo -e "${GREEN}✅ Root .env exists${NC}"
fi

echo ""

# Step 3: Create documents folder
echo -e "${YELLOW}Step 3: Preparing documents folder...${NC}"
mkdir -p documents
echo -e "${GREEN}✅ Documents folder ready${NC}"
echo ""

# Step 4: Build Docker images
echo -e "${YELLOW}Step 4: Building Docker images...${NC}"
echo "This may take 5-10 minutes on first run..."
echo ""

docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker images built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed. Please check the errors above.${NC}"
    exit 1
fi

echo ""

# Step 5: Start services
echo -e "${YELLOW}Step 5: Starting all services...${NC}"
echo ""

docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Services started${NC}"
else
    echo -e "${RED}❌ Failed to start services${NC}"
    exit 1
fi

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Step 6: Check service status
echo -e "${YELLOW}Step 6: Checking service status...${NC}"
echo ""

docker-compose ps

echo ""

# Step 7: Initialize database
echo -e "${YELLOW}Step 7: Initializing database...${NC}"
echo ""

docker-compose exec -T backend flask db upgrade || {
    echo -e "${YELLOW}⚠️  Migrations not found, creating initial migration...${NC}"
    docker-compose exec -T backend flask db init || true
    docker-compose exec -T backend flask db migrate -m "Initial migration" || true
    docker-compose exec -T backend flask db upgrade
}

echo -e "${GREEN}✅ Database initialized${NC}"
echo ""

# Step 8: Health check
echo -e "${YELLOW}Step 8: Checking service health...${NC}"
echo ""

sleep 5

if curl -s http://localhost:5000/jobs/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Backend health check failed. It may still be starting up.${NC}"
    echo "Wait a bit longer and check: curl http://localhost:5000/jobs/health"
fi

echo ""

# Step 9: Summary
echo "=========================================="
echo -e "${GREEN}Build Complete!${NC}"
echo "=========================================="
echo ""
echo "Services are running:"
echo "  • Frontend:  http://localhost:3000"
echo "  • Backend:   http://localhost:5000"
echo "  • Health:    http://localhost:5000/jobs/health"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. (Optional) Load documents:"
echo "     docker-compose exec backend python scripts/load_documents_from_folder.py --folder /documents"
echo "  3. Start topic discovery from the UI"
echo ""
echo "Useful commands:"
echo "  • View logs:        docker-compose logs -f [service-name]"
echo "  • Stop services:    docker-compose down"
echo "  • Restart service:  docker-compose restart [service-name]"
echo ""
echo "For detailed troubleshooting, see BUILD_GUIDE.md"
echo ""

