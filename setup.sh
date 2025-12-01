#!/bin/bash

# Setup script for Topic Discovery System

set -e

echo "Setting up Topic Discovery System..."

# Backend setup
echo "Setting up backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Initialize database migrations
if [ ! -d "migrations" ]; then
    flask db init
fi
flask db migrate -m "Initial migration"
flask db upgrade

# Frontend setup
echo "Setting up frontend..."
cd ../frontend
npm install

echo "Setup complete!"
echo ""
echo "To start development:"
echo "  Backend: cd backend && source venv/bin/activate && python run.py"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"

