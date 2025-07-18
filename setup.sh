#!/bin/bash

# Social Media Management Bot Setup Script
# This script helps set up the development environment

set -e

echo "🤖 Social Media Management Bot Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creating environment configuration...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Environment file created (.env)${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your actual configuration values${NC}"
else
    echo -e "${GREEN}✅ Environment file already exists${NC}"
fi

# Validate project structure
echo -e "${YELLOW}🔍 Validating project structure...${NC}"
python validate_structure.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Project structure validation failed${NC}"
    exit 1
fi

# Setup choice
echo ""
echo "Choose setup option:"
echo "1) Quick start with Docker (recommended)"
echo "2) Local development setup"
echo "3) Production deployment"
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo -e "${YELLOW}🐳 Starting with Docker Compose...${NC}"
        cd docker
        docker-compose up -d
        echo -e "${GREEN}✅ Application started successfully!${NC}"
        echo -e "${GREEN}📱 Frontend: http://localhost:3000${NC}"
        echo -e "${GREEN}🔧 Backend API: http://localhost:8000${NC}"
        echo -e "${GREEN}📚 API Docs: http://localhost:8000/docs${NC}"
        ;;
    2)
        echo -e "${YELLOW}💻 Setting up local development...${NC}"
        
        # Backend setup
        echo -e "${YELLOW}Setting up backend...${NC}"
        cd backend
        
        if [ ! -d "venv" ]; then
            python -m venv venv
            echo -e "${GREEN}✅ Virtual environment created${NC}"
        fi
        
        source venv/bin/activate
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Backend dependencies installed${NC}"
        
        cd ..
        
        # Frontend setup
        echo -e "${YELLOW}Setting up frontend...${NC}"
        cd frontend
        npm install
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
        
        cd ..
        
        echo -e "${GREEN}✅ Local development setup complete!${NC}"
        echo -e "${YELLOW}To start development:${NC}"
        echo "Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
        echo "Frontend: cd frontend && npm run dev"
        ;;
    3)
        echo -e "${YELLOW}🚀 Setting up production deployment...${NC}"
        cd docker
        docker-compose -f docker-compose.prod.yml up -d
        echo -e "${GREEN}✅ Production deployment started!${NC}"
        echo -e "${YELLOW}⚠️  Make sure to configure your reverse proxy and SSL certificates${NC}"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo -e "${YELLOW}📖 For more information, check the README.md file${NC}"