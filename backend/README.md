# RTAB-Map Object Localization & Search API

A production-ready RESTful API service built with FastAPI that leverages RTAB-Map SLAM technology for real-time object search, 6-DoF localization, and intelligent navigation guidance in mapped indoor environments.

## Overview

This containerized API system provides spatial intelligence capabilities for applications requiring object detection, position tracking, and navigation assistance in pre-mapped environments. The service processes camera images to determine precise location and orientation while simultaneously identifying and locating objects within the environment.

## Key Features

### Core Capabilities

- **🔍 Semantic Object Search**
  - Natural language queries for object discovery
  - Spatial indexing for efficient multi-frame searches
  - Returns object locations with coordinate data

- **📍 6-DoF Localization**
  - Real-time pose estimation (x, y, z, roll, pitch, yaw)
  - Vision-based position tracking using RTAB-Map SLAM
  - Sub-second processing with optimized parameters

- **🧭 Navigation Guidance**
  - Automatic distance and bearing calculations
  - Human-readable directional instructions
  - Proximity detection and multi-target handling

- **🎯 Integrated Workflow**
  - Unified search-and-localize endpoint
  - Automatic nearest target selection
  - Complete spatial awareness in single API call

### Technical Features

- **High-Performance Processing**
  - Asynchronous request handling
  - Concurrent multi-request support
  - Direct SQLite database queries for speed

- **Rich Metadata Integration**
  - Detailed scene descriptions
  - Object context and relationships
  - Frame-level pose data linkage

- **Production Architecture**
  - Docker Compose orchestration
  - Live code reload for development
  - External image mounting for flexibility
  - Embedded database for deployment

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check and version info |
| `/status` | GET | Detailed service status and capabilities |
| `/localize` | POST | Image-based localization only |
| `/search` | POST | Object search without localization |
| `/search-and-localize` | POST | Integrated search, localize, and navigate |

### Response Examples

**Localization Response:**
```json
{
  "x": 0.97, "y": 0.06, "z": 0.12,
  "roll": -2.08, "pitch": -1.57, "yaw": -1.50,
  "objects": "object_name: descriptors... •• object_name: descriptors...",
  "pic_id": 24,
  "localization_successful": true,
  "elapsed_ms": 4156.0
}
```

**Search-and-Localize Response:**
```json
{
  "success": true,
  "search_results": [
    {
      "frame_id": 2,
      "location": {"x": 0.98, "y": 0.04},
      "objects": ["object descriptions"]
    }
  ],
  "localization_results": {
    "position": {"x": 0.97, "y": 0.06, "z": 0.12},
    "orientation": {"roll": -2.08, "pitch": -1.57, "yaw": -1.50}
  },
  "navigation_guidance": {
    "direction": "ahead and to your right, approximately very close away",
    "distance": 0.02,
    "bearing": 22.7,
    "turn_instruction": "Turn 23° to your right",
    "is_at_location": true
  },
  "total_matches": 5,
  "workflow_status": "completed"
}
```

## Architecture

### Container Services

**rtabmap-core**
- Base RTAB-Map runtime environment
- Ubuntu 22.04 (Jammy) based image
- Provides SLAM processing capabilities

**rtabmap-api**
- FastAPI application server
- Python 3.10+ with async support
- Uvicorn ASGI server with auto-reload
- Embedded database at `/data/database.db`
- External test images at `/external_testimage`

### Technology Stack

- **Backend Framework:** FastAPI with Pydantic validation
- **SLAM Engine:** RTAB-Map (Real-Time Appearance-Based Mapping)
- **Database:** SQLite with spatial data and object metadata
- **Server:** Uvicorn ASGI with async processing
- **Containerization:** Docker & Docker Compose
- **Language:** Python 3.10+

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Pre-built RTAB-Map database file
- Test images for localization

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/kasrajb/rtabmap_api.git
   cd rtabmap_api
   ```

2. **Prepare Data**
   - Place your RTAB-Map database file in `./data/database/`
   - Add test images to `./data/test_images/`

3. **Build and Start Services**
   ```powershell
   docker-compose up --build -d
   ```

4. **Verify System Health**
   ```powershell
   curl http://localhost:8040/health
   ```

### Configuration

**Port Mapping:**
- API Service: `localhost:8040` → Container `8000`

**Volume Mounts:**
- Database: Embedded at `/data/database.db` in container
- Test Images: `./data/test_images` → `/external_testimage`
- Application Code: `.` → `/app` (for live reload)

## Usage Examples

### Health Check
```powershell
# Check API availability
curl http://localhost:8040/health

# Get detailed service status
curl http://localhost:8040/status
```

### Localization Only
```powershell
# Localize using test image
curl.exe -X POST http://localhost:8040/localize

# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:8040/localize" -Method POST
```

### Object Search
```powershell
# Search for an object
Invoke-RestMethod -Uri "http://localhost:8040/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"object_name": "chair"}'
```

### Integrated Search and Localize
```powershell
# Complete workflow: search + localize + navigate
Invoke-RestMethod -Uri "http://localhost:8040/search-and-localize" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"object_name": "door"}' | ConvertTo-Json -Depth 10
```

### Interactive CLI Mode
```powershell
# Run interactive search-and-localize script
python integrated_search_localize.py

# Or use the test script
.\test_api.ps1
```

## Development

### Project Structure

```
rtabmap_api/
├── app.py                          # FastAPI application entry point
├── rtabmap_service.py              # RTAB-Map SLAM integration
├── workflow_service.py             # Integrated workflow orchestration
├── search_product.py               # Object search functionality
├── navigation_guidance.py          # Navigation calculation logic
├── integrated_search_localize.py   # CLI interface
├── docker-compose.yml              # Service orchestration
├── Dockerfile                      # Container configuration
├── requirements.txt                # Python dependencies
└── data/
    ├── database/                   # RTAB-Map database storage
    └── test_images/                # External test images
```

### Live Development

The system supports hot-reload for rapid development:

```powershell
# Code changes are automatically detected
# No need to rebuild or restart containers
# Uvicorn watches /app directory for changes
```

### View Logs

```powershell
# View recent logs
docker compose logs --tail 50 rtabmap-api

# Follow logs in real-time
docker compose logs -f rtabmap-api

# View logs from last 15 seconds
docker compose logs --since 15s rtabmap-api
```

### Manual Service Restart

```powershell
# Restart API service only
docker compose restart rtabmap-api

# Restart all services
docker compose restart

# Rebuild and restart
docker compose down
docker compose up --build -d
```

## API Documentation

Interactive API documentation available at:
- **Swagger UI:** `http://localhost:8040/docs`
- **ReDoc:** `http://localhost:8040/redoc`

## Performance Metrics

- **Localization:** 3-5 seconds per image
- **Search Queries:** Sub-10ms with spatial indexing
- **Concurrent Support:** Multiple simultaneous requests
- **Memory Footprint:** ~2GB typical

---

**Version:** 1.1 | **Status:** Production Ready