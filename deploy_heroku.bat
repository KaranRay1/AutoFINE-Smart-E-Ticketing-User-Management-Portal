@echo off
echo ========================================
echo    AutoFINE - Heroku Deployment Helper
echo ========================================
echo.

REM Check if Heroku CLI is installed
heroku --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Heroku CLI is not installed!
    echo Please install from: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

echo [1/6] Checking Heroku login...
heroku auth:whoami >nul 2>&1
if errorlevel 1 (
    echo Please login to Heroku...
    heroku login
) else (
    echo Already logged in to Heroku.
)

echo.
echo [2/6] Checking Git repository...
if not exist .git (
    echo Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
) else (
    echo Git repository found.
)

echo.
echo [3/6] Checking for Heroku app...
heroku apps:info >nul 2>&1
if errorlevel 1 (
    echo No Heroku app found. Creating one...
    set /p APP_NAME="Enter your app name (or press Enter for auto-generated): "
    if "!APP_NAME!"=="" (
        heroku create
    ) else (
        heroku create %APP_NAME%
    )
) else (
    echo Heroku app already exists.
)

echo.
echo [4/6] Setting environment variables...
echo Setting SECRET_KEY...
heroku config:set SECRET_KEY=autofine-secret-key-2024-change-in-production
echo Setting GEMINI_API_KEY...
heroku config:set GEMINI_API_KEY=AIzaSyDhRmsMTyY6mRlZQylpk5OME1m-PDNrXiU

echo.
echo [5/6] Adding PostgreSQL database...
heroku addons:create heroku-postgresql:mini

echo.
echo [6/6] Deploying to Heroku...
echo This may take a few minutes...
git push heroku main
if errorlevel 1 (
    echo Trying master branch instead...
    git push heroku master
)

echo.
echo ========================================
echo    Deployment Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Initialize database: heroku run python init_database.py
echo 2. Open your app: heroku open
echo 3. View logs: heroku logs --tail
echo.
pause
