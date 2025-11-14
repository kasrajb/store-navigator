# Store Navigator - Unified Repository

This repository contains both the frontend and backend for the Store Navigator application.

## Repository Structure

```
store-navigator/
├── backend/              # RTAB-Map API backend (FastAPI + Docker)
│   ├── app.py           # Main FastAPI application
│   ├── Dockerfile       # Backend container configuration
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── data/            # Database and test images
├── index.html           # Frontend HTML (GitHub Pages)
├── script.js            # Frontend JavaScript
├── styles.css           # Frontend CSS
└── README.md            # Project documentation
```

## Deployment

### Frontend (GitHub Pages)
- **URL**: https://kasrajb.github.io/store-navigator/
- **Files**: `index.html`, `script.js`, `styles.css` in root directory
- **Auto-deploy**: Pushes to `main` branch automatically rebuild GitHub Pages

### Backend (Railway)
- **URL**: https://store-navigator-production.up.railway.app
- **Source**: `backend/` directory
- **Auto-deploy**: Pushes to `main` branch automatically redeploy Railway
- **Root Path**: Set Railway to use `backend/` as the root directory

## Railway Configuration

In Railway dashboard, configure:
1. **Root Directory**: `backend`
2. **Build Command**: `docker build -t rtabmap-api .`
3. **Start Command**: Use the Dockerfile CMD (uvicorn)

## Local Development

### Frontend
```bash
# Serve locally
cd store-navigator
python -m http.server 8080
# Open http://localhost:8080
```

### Backend
```bash
# Run with Docker
cd backend
docker-compose up
# API available at http://localhost:8040
```

## CORS Configuration

Backend allows requests from:
- `https://kasrajb.github.io` (GitHub Pages)
- `https://store-navigator-production.up.railway.app` (Railway backend)
- `http://localhost:8080` (local testing)
- `http://127.0.0.1:8080` (local testing)
- `http://172.20.10.2:8080` (phone hotspot testing)

## API Endpoints

- `GET /` - Root health check
- `GET /health` - Detailed health check
- `GET /status` - Service status
- `POST /search-and-localize` - Main localization endpoint

## Changes in This Update

1. ✅ Combined frontend and backend into single repository
2. ✅ Updated CORS to restrict origins (security)
3. ✅ Added root `/` endpoint for quick health checks
4. ✅ Updated frontend to use Railway backend URL
5. ✅ Added cache-busting (`?v=railway-deploy`) to force client updates
