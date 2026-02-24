$ErrorActionPreference = "Stop"

Write-Host "Starting Banking Service Assessment Environment..."

# 1. Check if Docker is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop or the Docker daemon and try again." -ForegroundColor Red
    exit 1
}

# 2. Build and stand up the environment
Write-Host "Building and starting Docker containers in detached mode..."
docker-compose up -d --build

# 3. Interactive prompt for database seeding
Write-Host ""
$seed_response = Read-Host "Would you like to seed the database with synthetic users and transactions? (y/n)"

if ($seed_response -match "^[Yy]$") {
    if (Test-Path "seed_data.py") {
        Write-Host "Running database seeder script..."
        Start-Sleep -Seconds 3
        docker-compose exec api python seed_data.py
        Write-Host "Database seeded successfully."
    } else {
        Write-Host "Warning: seed_data.py not found. Skipping data seeding..." -ForegroundColor Yellow
    }
} else {
    Write-Host "Skipping database seeding."
}

# 4. Print completion URIs
Write-Host ""
Write-Host "=========================================================="
Write-Host "🚀 Deployment Complete!"
Write-Host "=========================================================="
Write-Host "🌐 Frontend is live at: http://localhost:8080"
Write-Host "📚 API Docs are live at: http://localhost:8000/docs"
Write-Host "=========================================================="
Write-Host ""
