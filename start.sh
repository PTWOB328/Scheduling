#!/bin/bash
# Startup script for Squadron Scheduler

echo "Starting Squadron Scheduler..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "Docker found. Starting services with Docker Compose..."
    docker compose up -d
    
    echo "Waiting for database to be ready..."
    sleep 5
    
    echo "Running database migrations..."
    docker compose exec backend alembic upgrade head
    
    echo ""
    echo "✅ Application started!"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker compose logs -f"
    echo "To stop: docker compose down"
else
    echo "Docker not found. Please install Docker or use local development setup."
    exit 1
fi

