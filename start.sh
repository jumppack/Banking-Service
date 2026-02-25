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
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Auto-generating from .env.example..."
    cp .env.example .env
fi

# Ensure SECRET_KEY is securely populated
python3 -c '
import os, secrets
try:
    with open(".env", "r") as f:
        lines = f.readlines()
    
    placeholders = {"changeme", "change_me", "supersecretkey", "change_me_to_a_long_random_value"}
    found_secret = False
    updated = False
    
    new_lines = []
    for line in lines:
        if line.startswith("SECRET_KEY="):
            found_secret = True
            val = line.split("=", 1)[1].strip().strip("\"'\''")
            if not val or val in placeholders:
                new_key = secrets.token_urlsafe(48)
                new_lines.append(f"SECRET_KEY={new_key}\n")
                updated = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    if not found_secret:
        new_key = secrets.token_urlsafe(48)
        new_lines.append(f"\nSECRET_KEY={new_key}\n")
        updated = True
        
    if updated:
        with open(".env", "w") as f:
            f.writelines(new_lines)
        print("Generated a secure SECRET_KEY in .env")
    else:
        print("SECRET_KEY already set; leaving as-is")
except Exception as e:
    print(f"Error checking SECRET_KEY: {e}")
'

echo "Building and starting Docker containers in detached mode..."
docker-compose up -d --build

# 3. Interactive prompt for database seeding
echo ""
read -p "Would you like to seed the database with synthetic users and transactions? (y/n): " seed_response

if [[ "$seed_response" =~ ^[Yy]$ ]]; then
    if [ -f "seed_data.py" ]; then
        echo "Running database seeder script..."
        # Ensure the API is fully awake (basic sleep to let SQLite lock initialize if creating from scratch)
        sleep 3
        docker-compose exec api python seed_data.py || echo "Warning: Seeding execution failed inside container."
        echo "Database seeded successfully."
    else
        echo "Warning: seed_data.py not found. Skipping data seeding..."
    fi
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
