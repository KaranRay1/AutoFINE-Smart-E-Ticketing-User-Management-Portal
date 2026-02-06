# AutoFINE - Heroku Deployment Helper (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AutoFINE - Heroku Deployment Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Heroku CLI is installed
try {
    $herokuVersion = heroku --version 2>&1
    Write-Host "[1/6] Heroku CLI found: $herokuVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Heroku CLI is not installed!" -ForegroundColor Red
    Write-Host "Please install from: https://devcenter.heroku.com/articles/heroku-cli" -ForegroundColor Yellow
    exit 1
}

# Check Heroku login
Write-Host "[2/6] Checking Heroku login..." -ForegroundColor Yellow
try {
    heroku auth:whoami | Out-Null
    Write-Host "Already logged in to Heroku." -ForegroundColor Green
} catch {
    Write-Host "Please login to Heroku..." -ForegroundColor Yellow
    heroku login
}

# Check Git repository
Write-Host "[3/6] Checking Git repository..." -ForegroundColor Yellow
if (-not (Test-Path .git)) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
} else {
    Write-Host "Git repository found." -ForegroundColor Green
}

# Check for Heroku app
Write-Host "[4/6] Checking for Heroku app..." -ForegroundColor Yellow
try {
    heroku apps:info | Out-Null
    Write-Host "Heroku app already exists." -ForegroundColor Green
} catch {
    Write-Host "No Heroku app found. Creating one..." -ForegroundColor Yellow
    $appName = Read-Host "Enter your app name (or press Enter for auto-generated)"
    if ($appName -eq "") {
        heroku create
    } else {
        heroku create $appName
    }
}

# Set environment variables
Write-Host "[5/6] Setting environment variables..." -ForegroundColor Yellow
Write-Host "Setting SECRET_KEY..." -ForegroundColor Gray
heroku config:set SECRET_KEY=autofine-secret-key-2024-change-in-production
Write-Host "Setting GEMINI_API_KEY..." -ForegroundColor Gray
heroku config:set GEMINI_API_KEY=AIzaSyDhRmsMTyY6mRlZQylpk5OME1m-PDNrXiU

# Add PostgreSQL
Write-Host "[6/6] Adding PostgreSQL database..." -ForegroundColor Yellow
heroku addons:create heroku-postgresql:mini

# Deploy
Write-Host ""
Write-Host "Deploying to Heroku..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
try {
    git push heroku main
} catch {
    Write-Host "Trying master branch instead..." -ForegroundColor Yellow
    git push heroku master
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Initialize database: heroku run python init_database.py" -ForegroundColor White
Write-Host "2. Open your app: heroku open" -ForegroundColor White
Write-Host "3. View logs: heroku logs --tail" -ForegroundColor White
Write-Host ""
