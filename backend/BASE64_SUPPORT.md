# RTAB-Map API - Base64 Image Support

## Quick Reference

### API Endpoint: `/search-and-localize`

**Accepts TWO methods:**

1. **File Upload** (original)
   ```bash
   curl -X POST http://localhost:8040/search-and-localize \
     -F "object_name=door" \
     -F "image=@image.jpg"
   ```

2. **Base64 String** (new)
   ```bash
   curl -X POST http://localhost:8040/search-and-localize \
     -F "object_name=door" \
     -F "image_base64=/9j/4AAQSkZJRgABAQAA..."
   ```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Object to search for |
| `image` | file | Optional* | Image file upload |
| `image_base64` | string | Optional* | Base64-encoded image |
| `include_timing` | boolean | No | Include timing info (default: true) |

*Either `image` OR `image_base64` must be provided (not both)

### Base64 Format

Supports both formats:
- Raw Base64: `/9j/4AAQSkZJRgABAQAA...`
- Data URI: `data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA...`

### Test Scripts

```powershell
# PowerShell
.\test_base64_api.ps1

# Python
python test_base64_api.py
```

Update `TEST_IMAGE_PATH` before running.

### Deployment

```bash
cd rtabmap_api
docker-compose down
docker-compose up --build -d
docker-compose logs -f rtabmap-api
```
