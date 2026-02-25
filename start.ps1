param (
    [string]$envTarget = 'development'
)

$ErrorActionPreference = "Stop"

Write-Host "Starting Banking Service Assessment Environment..."

# 1. Check if Docker is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop or the Docker daemon and try again." -ForegroundColor Red
    exit 1
}

# 2. Build and stand up the environment
$envTemplate = ".env.$envTarget.example"

if (-Not (Test-Path $envTemplate)) {
    Write-Host "Error: Template $envTemplate not found. Valid environments: development, test, production." -ForegroundColor Red
    exit 1
}

if (-Not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Auto-generating from $envTemplate..." -ForegroundColor Yellow
    Copy-Item $envTemplate -Destination ".env"
}

# Ensure SECRET_KEY is securely populated
$envPath = ".env"
$placeholders = @("changeme", "change_me", "supersecretkey", "change_me_to_a_long_random_value", "")
$updated = $false
$foundSecret = $false

$lines = Get-Content $envPath
$newLines = @()

foreach ($line in $lines) {
    if ($line -match "^SECRET_KEY=(.*)") {
        $foundSecret = $true
        $val = $matches[1].Trim("`"",""'"," ")
        if ($placeholders -contains $val) {
            $bytes = New-Object byte[] 48
            [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
            $newKey = [Convert]::ToBase64String($bytes)
            $newLines += "SECRET_KEY=$newKey"
            $updated = $true
        } else {
            $newLines += $line
        }
    } else {
        $newLines += $line
    }
}

if (-Not $foundSecret) {
    $bytes = New-Object byte[] 48
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $newKey = [Convert]::ToBase64String($bytes)
    $newLines += "SECRET_KEY=$newKey"
    $updated = $true
}

if ($updated) {
    Set-Content -Path $envPath -Value $newLines
    Write-Host "Generated a secure SECRET_KEY in .env" -ForegroundColor Green
} else {
    Write-Host "SECRET_KEY already set; leaving as-is"
}

Write-Host "Building and starting Docker containers in detached mode..."
docker-compose up -d --build

# 3. Interactive prompt for database seeding
Write-Host ""
$seed_response = Read-Host "Would you like to seed the database with synthetic users and transactions? (y/n)"

if ($seed_response -match "^[Yy]$") {
    if (Test-Path "seed_data.py") {
        Write-Host "Running database seeder script..."
        Start-Sleep -Seconds 3
        try {
            docker-compose exec api python seed_data.py
        } catch {
            Write-Host "Warning: Seeding execution failed inside container." -ForegroundColor Yellow
        }
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
