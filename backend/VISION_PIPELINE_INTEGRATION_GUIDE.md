# Vision Pipeline Integration Guide

## Overview

The RTAB-Map API has been modified to accept **image uploads** via HTTP POST requests, enabling seamless integration with the vision pipeline. This document provides everything you need to integrate `vision_app.py` with the RTAB-Map localization and navigation system.

---

## What Changed

### Before (Hardcoded Test Images)
- API used images from `/external_testimage` directory
- Required manual file placement in Docker volume
- No dynamic image processing capability

### After (Dynamic Image Upload)
- API accepts image uploads via multipart/form-data
- Supports JPEG, PNG, and BMP formats
- Maximum file size: 10 MB
- Automatic temporary file handling and cleanup

---

## API Endpoint

### `/search-and-localize`

**Method:** `POST`  
**Content-Type:** `multipart/form-data`  
**URL:** `http://localhost:8040/search-and-localize`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | File | ✅ Yes | Image file for localization (JPEG, PNG, BMP) |
| `object_name` | String | ✅ Yes | Name of the object to search for (e.g., "door", "orange door") |
| `include_timing` | Boolean | ❌ No | Include timing information in response (default: true) |

#### Response Format

```json
{
  "success": true,
  "search_results": [
    {
      "frame_id": 45,
      "location": {"x": 0.90, "y": 0.07},
      "objects": ["orange door: Main entrance door with orange paint"],
      "distance_from_user": 2.3
    }
  ],
  "localization_results": {
    "position": {"x": 0.9, "y": 0.07, "z": -0.04},
    "orientation": {"roll": 0.07, "pitch": -0.43, "yaw": 0.17},
    "detected_objects": "orange door: Main entrance",
    "picture_id": 45,
    "processing_time_ms": 6100.5
  },
  "navigation_guidance": {
    "target_object": "orange door",
    "target_frame_id": 45,
    "direction": "ahead and to your right, approximately 2.3 meters away",
    "distance": 2.3,
    "bearing": 35.2,
    "turn_instruction": "Turn 35° to your right",
    "is_at_location": false
  },
  "nearest_frame_id": 45,
  "total_distance_to_target": 2.3,
  "multiple_frames_found": false,
  "total_matches": 1,
  "workflow_status": "completed",
  "timing_ms": {
    "search_duration": 8.5,
    "localization_duration": 6100.3,
    "total_duration": 6108.8
  }
}
```

---

## Vision Pipeline Integration

### Key Outputs for Navigation

The `navigation_guidance` object contains all the information needed for navigation:

```python
navigation_guidance = {
    "direction": "ahead and to your right, approximately 2.3 meters away",
    "distance": 2.3,  # meters
    "bearing": 35.2,  # degrees (relative to user's current orientation)
    "turn_instruction": "Turn 35° to your right",
    "is_at_location": false  # true if user is within 1 meter of target
}
```

### Python Integration Example

```python
import requests

def get_navigation_to_object(image_path: str, object_name: str):
    """
    Send image and object query to RTAB-Map API and get navigation guidance.
    
    Args:
        image_path: Path to the captured image
        object_name: Name of the object to find
        
    Returns:
        Dictionary with navigation information
    """
    url = "http://localhost:8040/search-and-localize"
    
    with open(image_path, 'rb') as img:
        files = {'image': (img.name, img, 'image/jpeg')}
        data = {
            'object_name': object_name,
            'include_timing': True
        }
        
        response = requests.post(url, files=files, data=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        
        if result['success'] and result['navigation_guidance']:
            nav = result['navigation_guidance']
            return {
                'direction': nav['direction'],
                'distance': nav['distance'],
                'bearing': nav['bearing'],
                'turn_instruction': nav['turn_instruction'],
                'is_at_location': nav['is_at_location']
            }
    
    return None

# Usage in vision_app.py
navigation = get_navigation_to_object("current_scene.jpg", "orange door")

if navigation:
    print(f"Direction: {navigation['direction']}")
    print(f"Distance: {navigation['distance']:.2f} meters")
    print(f"Turn: {navigation['turn_instruction']}")
    
    if navigation['is_at_location']:
        print("You have arrived at the target location!")
```

---

## Testing the Integration

### 1. Using the Provided Example Script

We've included a ready-to-use testing script:

```bash
python vision_integration_example.py <image_path> <object_name>

# Example:
python vision_integration_example.py data/test_images/45.jpg "door"
```

### 2. Using cURL

```bash
curl -X POST http://localhost:8040/search-and-localize \
  -F "image=@data/test_images/45.jpg" \
  -F "object_name=door" \
  -F "include_timing=true"
```

### 3. Using Python Requests

```python
import requests

with open('data/test_images/45.jpg', 'rb') as img:
    files = {'image': img}
    data = {'object_name': 'door', 'include_timing': True}
    response = requests.post('http://localhost:8040/search-and-localize', 
                           files=files, data=data)
    
print(response.json())
```

---

## Error Handling

### Common Errors

| Status Code | Error | Solution |
|-------------|-------|----------|
| 400 | Invalid image format | Use JPEG, PNG, or BMP format |
| 400 | File too large | Reduce image size to under 10 MB |
| 404 | Object not found | Check object name spelling or try broader search term |
| 500 | Processing failed | Check logs for details; image may be corrupted |
| 503 | Service unavailable | Ensure Docker containers are running |

### Example Error Response

```json
{
  "detail": "Invalid image format. Allowed formats: JPEG, PNG, BMP. Received: image/gif"
}
```

---

## Image Requirements

### Supported Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)

### Size Limits
- **Maximum file size:** 10 MB
- **Recommended resolution:** 640x480 to 1920x1080
- **Minimum resolution:** 320x240

### Quality Guidelines
- Avoid blurry or motion-blurred images
- Ensure adequate lighting
- Include distinctive features for better localization
- Similar perspective to database images improves accuracy

---

## Backward Compatibility

The API maintains backward compatibility:

- **`/localize` endpoint:** Still uses test images from `/external_testimage`
- **Standalone CLI script:** Continues to work with external test images
- **Existing clients:** Not affected by this change

---

## Performance Considerations

### Typical Response Times

| Operation | Duration |
|-----------|----------|
| Object Search | 5-15 ms |
| Image Upload | 10-50 ms |
| RTAB-Map Localization | 5-8 seconds |
| Navigation Calculation | <1 ms |
| **Total End-to-End** | **~6-8 seconds** |

### Optimization Tips

1. **Image Size:** Compress images before upload to reduce transfer time
2. **Specific Searches:** Use precise object names (e.g., "orange door" vs "door")
3. **Reuse Connections:** Keep HTTP connections alive for multiple requests
4. **Async Processing:** Consider async/await patterns for non-blocking operations

---

## Architecture Overview

```
┌─────────────────┐
│  vision_app.py  │
│  (Your Code)    │
└────────┬────────┘
         │ HTTP POST (multipart/form-data)
         │ image + object_name
         ▼
┌─────────────────────────────────────────┐
│  RTAB-Map API (FastAPI)                 │
│  http://localhost:8040                  │
├─────────────────────────────────────────┤
│  1. Validate image (format, size)       │
│  2. Save to temp file                   │
│  3. Search database for object          │
│  4. Perform localization                │
│  5. Calculate navigation guidance       │
│  6. Clean up temp file                  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Response JSON                          │
├─────────────────────────────────────────┤
│  • search_results (locations)           │
│  • localization_results (pose)          │
│  • navigation_guidance (← USE THIS!)    │
│    - direction (human-readable)         │
│    - distance (meters)                  │
│    - bearing (degrees)                  │
│    - turn_instruction (action)          │
│    - is_at_location (boolean)           │
└─────────────────────────────────────────┘
```

---

## Complete Vision Pipeline Workflow

### Step-by-Step Integration

1. **Capture Image** (Vision Pipeline)
   ```python
   camera.capture_image("scene.jpg")
   ```

2. **Query User for Object** (Voice/Text Input)
   ```python
   object_name = input("What are you looking for? ")  # e.g., "orange door"
   ```

3. **Send to RTAB-Map API**
   ```python
   navigation = get_navigation_to_object("scene.jpg", object_name)
   ```

4. **Provide Navigation Guidance** (Audio/Visual Output)
   ```python
   if navigation:
       speak(navigation['direction'])
       speak(navigation['turn_instruction'])
       
       if navigation['is_at_location']:
           speak("You have arrived!")
   ```

5. **Update Display** (Optional Visual Feedback)
   ```python
   display_arrow(navigation['bearing'])
   display_distance(navigation['distance'])
   ```

---

## Troubleshooting

### Issue: "Service not available" (503 error)

**Solution:**
```bash
# Check if Docker containers are running
docker ps

# Expected output:
# rtabmap-core
# rtabmap-api (port 8040)

# Restart if needed
docker-compose up -d
```

### Issue: "Invalid image format" (400 error)

**Solution:**
- Verify image file is JPEG, PNG, or BMP
- Check file is not corrupted: `file image.jpg`
- Re-save image in correct format

### Issue: "Localization failed"

**Possible Causes:**
- Image doesn't match mapped environment
- Poor image quality or lighting
- No distinctive features visible
- Camera perspective too different from database images

**Solution:**
- Capture image from similar angle as mapping
- Ensure good lighting conditions
- Include identifiable landmarks
- Check logs: `docker logs rtabmap-api`

### Issue: Slow response times (>10 seconds)

**Solution:**
- Reduce image resolution before upload
- Check system resources: `docker stats`
- Verify database file is on fast storage (SSD)
- Consider increasing Docker memory allocation

---

## Support and Logs

### View API Logs
```bash
docker logs -f rtabmap-api
```

### View RTAB-Map Core Logs
```bash
docker logs -f rtabmap-core
```

### Health Check
```bash
curl http://localhost:8040/health
```

### Status Check
```bash
curl http://localhost:8040/status
```

---

## Summary

The RTAB-Map API now accepts **dynamic image uploads** and returns comprehensive **navigation guidance** for integration with your vision pipeline.

### Key Integration Points:

✅ **Endpoint:** `POST http://localhost:8040/search-and-localize`  
✅ **Input:** Image file + Object name  
✅ **Output:** Navigation guidance (direction, distance, bearing, turn instruction)  
✅ **Example Script:** `vision_integration_example.py`  
✅ **Error Handling:** Validates format, size, and integrity  
✅ **Performance:** ~6-8 seconds end-to-end  

**Next Step:** Test with `python vision_integration_example.py data/test_images/45.jpg "door"`

---

## Questions or Issues?

Check the logs first, then refer to:
- System Documentation: `RTABMAP_API_SYSTEM_DOCUMENTATION.md`
- README: `README.md`
- API Docs: `http://localhost:8040/docs` (when running)
