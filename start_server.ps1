# AutoFINE Server Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AutoFINE Server Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Get local IP address
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    ($_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*") -and $_.InterfaceAlias -notlike "*Loopback*"
}).IPAddress | Select-Object -First 1

if (-not $localIP) {
    $localIP = "localhost"
}

Write-Host "Local Access: http://localhost:5000" -ForegroundColor Green
Write-Host "Network Access: http://$localIP:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Server is starting... Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python app.py
