# Railway Deployment Setup Guide

## Quick Setup (3 Steps)

### 1. Configure Root Directory
In Railway dashboard → Settings → Root Directory:
```
backend
```

### 2. Add Database Volume (CRITICAL!)
Since the database file is too large for git (447 MB), you need to upload it to Railway's persistent storage:

**Method A: Using Railway CLI (Recommended)**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Upload database to volume
railway volume add data
railway volume upload data corridor-V3.db:/data/database.db
```

**Method B: Using Railway Dashboard**
1. Go to your Railway project
2. Click "Variables" tab
3. Add a new volume mount:
   - **Mount Path**: `/data`
   - **Name**: `rtabmap-data`
4. Upload `corridor-V3.db` via Railway's file upload interface
5. Ensure it's at `/data/database.db` in the container

**Method C: Use a Smaller Test Database (Quick Test)**
For initial testing, you can use a smaller database or mock data. Update `app.py` to handle missing database gracefully.

### 3. Set Environment Variables
In Railway → Variables:
```
PORT=8000
DATA_DIR=/data
PYTHONUNBUFFERED=1
```

Railway automatically sets `PORT`, but we explicitly use 8000 in our Dockerfile.

## Database File Locations

- **Local Development**: `backend/data/database/corridor-V3.db`
- **Railway Container**: `/data/database.db` (via persistent volume)
- **File Size**: ~447 MB (too large for git)

## Verification Steps

After deployment completes:

1. **Check Deploy Logs**: Should see "RTAB-Map service initialized successfully"
2. **Test Root Endpoint**: 
   ```bash
   curl https://store-navigator-production.up.railway.app/
   ```
   Expected: `{"service": "rtabmap-api", "status": "running", ...}`

3. **Test Health Endpoint**:
   ```bash
   curl https://store-navigator-production.up.railway.app/health
   ```
   Expected: `{"status": "ok", ...}`

## Troubleshooting

### Build Fails: "No database in build context"
✅ Expected behavior! The Dockerfile will now continue without the database file. You need to upload it to the volume (see Step 2).

### Deploy Fails: "Database not found: /data/database.db"
❌ The database volume is not mounted or file is missing.
- Check that volume is mounted at `/data`
- Verify file exists at `/data/database.db` in container

### App Starts But Returns 500 Errors
❌ Check deploy logs for initialization errors
- Database might be corrupted
- Test image directory might be missing
- RTAB-Map initialization failed

## Files Changed for Railway

1. **Dockerfile**: Made database copy optional (won't fail build if missing)
2. **railway.json**: Railway-specific configuration
3. **app.py**: Already configured correctly (uses `/data/database.db`)

## Port Configuration

- **Container Internal**: 8000 (hardcoded in Dockerfile CMD)
- **Railway External**: Automatically assigned and proxied by Railway
- **Railway URL**: `https://store-navigator-production.up.railway.app`

## Next Steps After Deployment

1. ✅ Verify endpoints respond (see Verification Steps above)
2. ✅ Test from frontend: https://kasrajb.github.io/store-navigator/
3. ✅ Test on phone with camera
4. ✅ Check Railway metrics for performance

## Cost Considerations

- Database is ~447 MB → requires persistent storage
- RTAB-Map image processing is CPU/memory intensive
- Monitor Railway usage to stay within free tier or budget
