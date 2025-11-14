# Railway Database Upload Script
# Run this script to upload the database to Railway

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Railway Database Upload Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Railway CLI is installed
$railwayCli = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayCli) {
    Write-Host "❌ Railway CLI not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Railway CLI first:" -ForegroundColor Yellow
    Write-Host "npm install -g @railway/cli" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or use the Railway dashboard to upload the database manually:" -ForegroundColor Yellow
    Write-Host "1. Go to https://railway.app/project/your-project" -ForegroundColor Yellow
    Write-Host "2. Click 'Volumes' tab" -ForegroundColor Yellow
    Write-Host "3. Create a volume mounted at /data" -ForegroundColor Yellow
    Write-Host "4. Upload corridor-V3.db to /data/database.db" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Railway CLI found" -ForegroundColor Green
Write-Host ""

# Check if database file exists
$dbPath = Join-Path $PSScriptRoot "backend\data\database\corridor-V3.db"

if (-not (Test-Path $dbPath)) {
    Write-Host "❌ Database file not found at:" -ForegroundColor Red
    Write-Host $dbPath -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure the database file exists in backend/data/database/" -ForegroundColor Yellow
    exit 1
}

$dbSizeMB = [math]::Round((Get-Item $dbPath).Length / 1MB, 2)
Write-Host "✅ Database file found: $dbSizeMB MB" -ForegroundColor Green
Write-Host ""

# Instructions
Write-Host "Follow these steps to upload the database:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Login to Railway:" -ForegroundColor Yellow
Write-Host "   railway login" -ForegroundColor White
Write-Host ""
Write-Host "2. Link to your project:" -ForegroundColor Yellow
Write-Host "   railway link" -ForegroundColor White
Write-Host "   (Select: store-navigator-production)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Create a volume (if not exists):" -ForegroundColor Yellow
Write-Host "   railway volume create" -ForegroundColor White
Write-Host "   Name: rtabmap-data" -ForegroundColor Gray
Write-Host "   Mount Path: /data" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Upload the database:" -ForegroundColor Yellow
Write-Host "   cd backend/data/database" -ForegroundColor White
Write-Host "   railway run --volume rtabmap-data:/data cp corridor-V3.db /data/database.db" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Would you like to copy the Railway commands to clipboard? (Y/N)"

if ($choice -eq 'Y' -or $choice -eq 'y') {
    $commands = @"
railway login
railway link
cd backend/data/database
railway run --volume rtabmap-data:/data cp corridor-V3.db /data/database.db
"@
    Set-Clipboard -Value $commands
    Write-Host "✅ Commands copied to clipboard!" -ForegroundColor Green
    Write-Host "Paste them into your terminal one by one." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Alternative: Use Railway Dashboard (Easier)" -ForegroundColor Cyan
Write-Host "1. Go to https://railway.app" -ForegroundColor Yellow
Write-Host "2. Open your project: store-navigator-production" -ForegroundColor Yellow
Write-Host "3. Go to 'Volumes' tab" -ForegroundColor Yellow
Write-Host "4. Add volume: /data" -ForegroundColor Yellow
Write-Host "5. Upload corridor-V3.db via web interface" -ForegroundColor Yellow
Write-Host "6. Rename to database.db in the volume" -ForegroundColor Yellow
