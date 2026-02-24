#!/bin/bash

# Exit on any failure
set -e

echo "Starting Banking Service Assessment Environment..."

# 1. Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running. Please start Docker Desktop or the Docker daemon and try again."
  exit 1
fi

# 2. Build and stand up the environment
echo "Building and starting Docker containers in detached mode..."
docker-compose up -d --build

# 3. Interactive prompt for database seeding
echo ""
read -p "Would you like to seed the database with synthetic users and transactions? (y/n): " seed_response

if [[ "$seed_response" =~ ^[Yy]$ ]]; then
    echo "Running database seeder script..."
    # Ensure the API is fully awake (basic sleep to let SQLite lock initialize if creating from scratch)
    sleep 3
    docker-compose exec api python seed_data.py
    echo "Database seeded successfully."
else
    echo "Skipping database seeding."
fi

# 4. Print completion URIs
echo ""
echo "=========================================================="
echo "🚀 Deployment Complete!"
echo "=========================================================="
echo "🌐 Frontend is live at: http://localhost:8080"
echo "📚 API Docs are live at: http://localhost:8000/docs"
echo "=========================================================="
echo ""
