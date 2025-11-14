# PowerShell script to test Base64 image upload to RTAB-Map API

Write-Host "=== RTAB-Map Base64 Image Test ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$API_URL = "http://localhost:8040/search-and-localize"
$TEST_IMAGE_PATH = ".\data\test_images\test.jpg"  # Update with your test image path
$OBJECT_NAME = "door"  # Update with object to search for

# Check if test image exists
if (-not (Test-Path $TEST_IMAGE_PATH)) {
    Write-Host "❌ Test image not found at: $TEST_IMAGE_PATH" -ForegroundColor Red
    Write-Host "Please update TEST_IMAGE_PATH in this script" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Found test image: $TEST_IMAGE_PATH" -ForegroundColor Green

# Read image and convert to Base64
Write-Host "Converting image to Base64..." -ForegroundColor Yellow
$imageBytes = [System.IO.File]::ReadAllBytes($TEST_IMAGE_PATH)
$base64String = [System.Convert]::ToBase64String($imageBytes)

Write-Host "✓ Base64 conversion complete" -ForegroundColor Green
Write-Host "  Image size: $($imageBytes.Length) bytes" -ForegroundColor Gray
Write-Host "  Base64 length: $($base64String.Length) characters" -ForegroundColor Gray
Write-Host ""

# Test 1: Base64 string only
Write-Host "Test 1: Sending Base64 image to API..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri $API_URL `
        -Method POST `
        -ContentType "multipart/form-data" `
        -Form @{
            object_name = $OBJECT_NAME
            image_base64 = $base64String
            include_timing = "true"
        }
    
    Write-Host "✓ API call successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Response ===" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10
    
} catch {
    Write-Host "❌ API call failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host ""
        Write-Host "Error details:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
