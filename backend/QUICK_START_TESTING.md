# Quick Start - Testing Image Upload Integration

## 🚀 Ready to Test in 3 Steps

### Step 1: Ensure Service is Running
```bash
# Check if containers are running
docker ps

# You should see:
# - rtabmap-core
# - rtabmap-api (port 8040)

# If not running, start them:
docker-compose up -d
```

### Step 2: Run the Test Script
```bash
# Test with existing test image
python vision_integration_example.py data/test_images/45.jpg "door"

# Expected output:
# ============================================================
# RTAB-MAP API RESPONSE
# ============================================================
# 
# [SEARCH RESULTS]
# Success: True
# Total Matches: 1
# 
# [LOCALIZATION RESULTS]
# Current Position: (x, y, z)
# Current Orientation: Roll, Pitch, Yaw
# 
# [NAVIGATION GUIDANCE]
# Target Object: door
# Direction: ahead and to your right, approximately X.X meters away
# Distance: X.X meters
# Bearing: X.X degrees
# Turn Instruction: Turn X° to your right/left
```

### Step 3: Test with Your Own Image
```bash
# Capture an image from your vision pipeline
# Then test:
python vision_integration_example.py path/to/your/image.jpg "object_name"
```

---

## 🧪 Quick Tests

### Test 1: Valid JPEG Image
```bash
python vision_integration_example.py data/test_images/45.jpg "door"
```
**Expected:** Success response with navigation guidance

### Test 2: Invalid Format (should fail gracefully)
```bash
# Create a test GIF file
python vision_integration_example.py test.gif "door"
```
**Expected:** Error message about invalid format

### Test 3: Using cURL
```bash
curl -X POST http://localhost:8040/search-and-localize \
  -F "image=@data/test_images/45.jpg" \
  -F "object_name=door" \
  -F "include_timing=true"
```
**Expected:** JSON response with navigation guidance

---

## 📝 What to Look For

### ✅ Success Indicators
- Response status: 200 OK
- `success: true` in response
- `navigation_guidance` object present
- Distance, bearing, and turn_instruction populated
- Processing time ~5-8 seconds

### ❌ Failure Indicators
- Response status: 400, 500, or 503
- `success: false` in response
- Error message in response body
- Check logs: `docker logs rtabmap-api`

---

## 🔍 Check Logs

### View API Logs
```bash
docker logs -f rtabmap-api
```

**Look for:**
- `"Received image upload: <filename>"`
- `"Image validation passed: X.XX MB"`
- `"Saved uploaded image to: /data/temp_uploads/..."`
- `"Workflow completed with status: completed"`
- `"Cleaned up temporary image: ..."`

---

## 🎯 Vision Pipeline Integration

### Python Code (Copy-Paste Ready)
```python
import requests

def get_navigation(image_path, object_name):
    """Send image to RTAB-Map API and get navigation guidance."""
    url = "http://localhost:8040/search-and-localize"
    
    with open(image_path, 'rb') as img:
        files = {'image': (img.name, img, 'image/jpeg')}
        data = {'object_name': object_name, 'include_timing': True}
        response = requests.post(url, files=files, data=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result['navigation_guidance']:
            return result['navigation_guidance']
    
    return None

# Usage
nav = get_navigation("captured_image.jpg", "orange door")
if nav:
    print(f"Direction: {nav['direction']}")
    print(f"Distance: {nav['distance']:.2f} meters")
    print(f"Turn: {nav['turn_instruction']}")
    print(f"At location: {nav['is_at_location']}")
```

---

## ⚠️ Common Issues

### Issue: "Connection refused"
**Solution:** Start Docker containers
```bash
docker-compose up -d
```

### Issue: "Invalid image format"
**Solution:** Use JPEG, PNG, or BMP only
```bash
# Convert image to JPEG
convert input.gif output.jpg
```

### Issue: "File not found"
**Solution:** Check image path is correct
```bash
# Use absolute path or relative from project root
python vision_integration_example.py ./data/test_images/45.jpg "door"
```

---

## 📊 Expected Performance

| Metric | Value |
|--------|-------|
| Image Upload | ~50ms |
| Object Search | ~10ms |
| Localization | ~5-8 seconds |
| Navigation Calc | <1ms |
| **Total Time** | **~6-8 seconds** |

---

## ✅ Success Criteria

Test is successful if you see:
1. ✅ HTTP 200 status code
2. ✅ `success: true` in response
3. ✅ `navigation_guidance` object present
4. ✅ All navigation fields populated:
   - `direction` (string)
   - `distance` (float, meters)
   - `bearing` (float, degrees)
   - `turn_instruction` (string)
   - `is_at_location` (boolean)
5. ✅ Processing time under 10 seconds
6. ✅ No errors in logs
7. ✅ Temporary files cleaned up (check logs)

---

## 🎓 Next Steps

After successful testing:
1. ✅ Integrate into `vision_app.py`
2. ✅ Test with real camera captures
3. ✅ Add audio feedback for navigation
4. ✅ Implement visual indicators (arrows, distance)
5. ✅ Add error handling for edge cases

---

## 📚 Full Documentation

- **Integration Guide:** `VISION_PIPELINE_INTEGRATION_GUIDE.md`
- **Changes Summary:** `CHANGES_SUMMARY.md`
- **System Docs:** `RTABMAP_API_SYSTEM_DOCUMENTATION.md`
- **API Docs:** http://localhost:8040/docs (when running)

---

**Ready to Go!** 🎉

Run: `python vision_integration_example.py data/test_images/45.jpg "door"`
