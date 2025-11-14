# RTAB-Map API Test Script with Beautiful Formatting
# Usage: .\test_api.ps1

function Format-ApiResponse {
    param($response)
    
    Write-Host "=== API Response ===" -ForegroundColor Green
    Write-Host "Success: $($response.success)" -ForegroundColor Cyan
    
    Write-Host "`nSearch Results ($($response.total_matches) matches):" -ForegroundColor Yellow
    foreach($result in $response.search_results) {
        Write-Host "  Frame $($result.frame_id): x=$($result.location.x), y=$($result.location.y)" -ForegroundColor White
        foreach($obj in $result.objects) {
            Write-Host "    → $obj" -ForegroundColor Gray
        }
    }
    
    Write-Host "`nLocalization Results:" -ForegroundColor Yellow
    $pos = $response.localization_results.position
    $ori = $response.localization_results.orientation
    Write-Host "  Position: {x=$($pos.x), y=$($pos.y), z=$($pos.z)}" -ForegroundColor White
    Write-Host "  Orientation: {roll=$($ori.roll), pitch=$($ori.pitch), yaw=$($ori.yaw)}" -ForegroundColor White
    Write-Host "  Picture ID: $($response.localization_results.picture_id)" -ForegroundColor White
    Write-Host "  Processing Time: $($response.localization_results.processing_time_ms)ms" -ForegroundColor White
    
    Write-Host "`nTiming: {search=$($response.timing_ms.search_duration)ms, localization=$($response.timing_ms.localization_duration)ms, total=$($response.timing_ms.total_duration)ms}" -ForegroundColor Magenta
    
    # Show detected objects in a more readable format
    if ($response.localization_results.detected_objects) {
        Write-Host "`nDetected Objects:" -ForegroundColor Yellow
        $objects = $response.localization_results.detected_objects -split "••"
        foreach($obj in $objects[0..5]) {  # Show first 6 objects
            if ($obj.Trim()) {
                Write-Host "  • $($obj.Trim())" -ForegroundColor Gray
            }
        }
        if ($objects.Count -gt 6) {
            Write-Host "  ... and $($objects.Count - 6) more objects" -ForegroundColor DarkGray
        }
    }
}

# Function to show search results immediately
function Show-SearchResults {
    param($searchResults, $objectName)
    
    Write-Host "Searching for `"$objectName`"...`n" -ForegroundColor White
    
    Write-Host "--- Search Results ---" -ForegroundColor Yellow
    if ($searchResults.Count -eq 0) {
        Write-Host "No products found matching your search." -ForegroundColor Gray
    } else {
        Write-Host "Found $($searchResults.Count) matches:`n" -ForegroundColor White
        
        for ($i = 0; $i -lt $searchResults.Count; $i++) {
            $result = $searchResults[$i]
            Write-Host "$($i + 1). Frame $($result.frame_id)" -ForegroundColor White
            Write-Host "   Location: x=$($result.location.x), y=$($result.location.y)" -ForegroundColor Gray
            
            foreach($obj in $result.objects) {
                Write-Host "   → $obj" -ForegroundColor Gray
            }
            Write-Host ""
        }
    }
}

# Function to show localization results
function Show-LocalizationResults {
    param($localizationResults)
    
    Write-Host "--- Localization Results ---" -ForegroundColor Yellow
    
    $pos = $localizationResults.position
    $ori = $localizationResults.orientation
    
    Write-Host "Position: x=$($pos.x), y=$($pos.y), z=$($pos.z)" -ForegroundColor White
    Write-Host "Orientation: roll=$($ori.roll), pitch=$($ori.pitch), yaw=$($ori.yaw)" -ForegroundColor White
    
    if ($localizationResults.detected_objects) {
        Write-Host "Detected Objects: $($localizationResults.detected_objects)" -ForegroundColor Gray
    }
    
    Write-Host "Picture ID: $($localizationResults.picture_id)" -ForegroundColor White
    Write-Host "Processing Time: $($localizationResults.processing_time_ms)ms" -ForegroundColor White
}

# Main script execution
Write-Host "=== RTAB-Map Object Search & Localization System ===" -ForegroundColor Cyan
Write-Host ""

# Get object name from user
$objectName = Read-Host "Enter the object you want to search for"

if (-not $objectName) {
    Write-Host "Please enter a search term." -ForegroundColor Red
    exit 1
}

try {
    Write-Host ""
    Write-Host "Searching for `"$objectName`"...`n" -ForegroundColor White
    
    # Use the integrated search-and-localize endpoint with navigation guidance
    $response = Invoke-RestMethod -Uri "http://localhost:8040/search-and-localize" -Method POST -Headers @{"Content-Type" = "application/json"} -Body "{`"object_name`": `"$objectName`"}"
    
    # Show search results with distance information
    Write-Host "--- Search Results ---" -ForegroundColor Yellow
    if ($response.search_results.Count -eq 0) {
        Write-Host "No products found matching your search." -ForegroundColor Gray
    } else {
        Write-Host "Found $($response.total_matches) matches:`n" -ForegroundColor White
        
        # Show multiple frames message if applicable
        if ($response.multiple_frames_found) {
            Write-Host "⚠️  The object exists in several frames. I will guide you to the nearest frame.`n" -ForegroundColor Yellow
        }
        
        for ($i = 0; $i -lt $response.search_results.Count; $i++) {
            $result = $response.search_results[$i]
            $nearestMarker = ""
            $distanceText = ""
            
            # Check if this is the nearest frame
            if ($response.nearest_frame_id -eq $result.frame_id) {
                $nearestMarker = " ⭐ NEAREST FRAME"
            }
            
            # Add distance information if available
            if ($result.distance_from_user -ne $null) {
                $distanceText = " ($($result.distance_from_user.ToString('0.00'))m away)"
            }
            
            Write-Host "$($i + 1). Frame $($result.frame_id)$nearestMarker$distanceText" -ForegroundColor White
            Write-Host "   Location: x=$($result.location.x), y=$($result.location.y)" -ForegroundColor Gray
            
            foreach($obj in $result.objects) {
                Write-Host "   → $obj" -ForegroundColor Gray
            }
            Write-Host ""
        }
    }
    
    Write-Host "Triggering localization..." -ForegroundColor White
    
    # Show localization results
    Write-Host "--- Localization Results ---" -ForegroundColor Yellow
    
    $pos = $response.localization_results.position
    $ori = $response.localization_results.orientation
    
    Write-Host "Position: x=$($pos.x), y=$($pos.y), z=$($pos.z)" -ForegroundColor White
    Write-Host "Orientation: roll=$($ori.roll), pitch=$($ori.pitch), yaw=$($ori.yaw)" -ForegroundColor White
    
    if ($response.localization_results.detected_objects) {
        Write-Host "Detected Objects: $($response.localization_results.detected_objects)" -ForegroundColor Gray
    }
    
    Write-Host "Picture ID: $($response.localization_results.picture_id)" -ForegroundColor White
    Write-Host "Processing Time: $($response.localization_results.processing_time_ms)ms" -ForegroundColor White
    
    # Show navigation guidance if available
    if ($response.navigation_guidance) {
        Write-Host "`n--- Navigation Guidance ---" -ForegroundColor Yellow
        $nav = $response.navigation_guidance
        Write-Host "🎯 Target: $($nav.target_object) (Frame $($nav.target_frame_id))" -ForegroundColor White
        Write-Host "📍 Direction: $($nav.direction)" -ForegroundColor White
        Write-Host "🧭 Turn Instruction: $($nav.turn_instruction)" -ForegroundColor White
        Write-Host "📏 Distance: $($nav.distance) meters" -ForegroundColor White
        
        if ($nav.is_at_location) {
            Write-Host "`nYou are already at the object location!" -ForegroundColor Green
        }
    }
    
    Write-Host "`n=== Workflow Complete ===" -ForegroundColor Green
    
} catch {
    Write-Host "`nError: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure the Docker container is running on port 8040" -ForegroundColor Yellow
    Write-Host "`n=== Workflow Failed ===" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green