# Railway Dashboard - Database Upload Guide

## 📦 Upload Database Without CLI (Easiest Method!)

Since npm/Railway CLI isn't available, use the Railway web dashboard - it's actually simpler!

---

## 🎯 Step-by-Step Instructions

### Step 1: Configure Root Directory (Do This FIRST!)

1. Go to: https://railway.app
2. Open your project: **store-navigator-production**
3. Click on your service (should see the deployment)
4. Click **"Settings"** tab
5. Find **"Root Directory"** setting
6. Enter: `backend`
7. Click **"Save"** or update
8. Railway will automatically redeploy

**Why?** Railway needs to know your app is in the `backend/` folder, not the root.

---

### Step 2: Wait for Current Build to Complete

Check the **"Deployments"** tab. Wait until you see:
- ✅ Build succeeded (the Dockerfile fix allows this now)
- ❌ Deploy may fail with "database not found" - this is expected!

---

### Step 3: Add Persistent Volume for Database

1. In your Railway project, click **"+ New"** button (top right)
2. Select **"Empty Service"** or **"Volume"** (depending on Railway UI version)
3. Or find **"Volumes"** in the left sidebar
4. Click **"+ New Volume"**
5. Configure:
   - **Name**: `rtabmap-data` (or any name you prefer)
   - **Mount Path**: `/data`
6. Click **"Create"**

---

### Step 4: Attach Volume to Your Service

1. Go back to your **store-navigator** service
2. Click **"Settings"** tab
3. Scroll to **"Volumes"** section
4. Click **"+ Add Volume"**
5. Select the volume you just created (`rtabmap-data`)
6. Mount path: `/data`
7. Save

---

### Step 5: Upload Database File

**Option A: Via Railway Dashboard (if available)**
Some Railway interfaces allow direct file upload:
1. Click on the volume
2. Look for "Upload" or "Files" option
3. Upload `corridor-V3.db` from:
   ```
   C:\Users\kasra\Desktop\Kasra\Telegram\Fall 2025\ECSE 542 Milestone #3\store-navigator\backend\data\database\corridor-V3.db
   ```
4. Rename to: `database.db` in the volume

**Option B: Use Railway's Web Terminal (Recommended)**
1. In your service, click **"Settings"**
2. Find **"Deploy"** section
3. Enable **"Web Terminal"** or **"Shell Access"** if available
4. Open the terminal
5. You'll need to upload via another method (see Option C)

**Option C: Temporary Upload Service (Alternative)**

Since direct upload might be limited, here's a workaround:

1. **Create a temporary upload endpoint in your app:**
   - Add a simple file upload endpoint to `app.py`
   - Upload the database via POST request
   - Then disable/remove the endpoint

2. **Use a file hosting service:**
   - Upload `corridor-V3.db` to Google Drive / Dropbox / WeTransfer
   - Generate a direct download link
   - Use Railway's terminal to `wget` or `curl` the file into `/data/database.db`

**Option D: Contact Railway Support**
If volumes don't show upload option:
- Railway support can help you upload large files
- They might provide temporary credentials for file transfer

---

### Step 6: Verify Database is in Place

**Using Railway Terminal (if available):**
```bash
ls -lh /data/
# Should show database.db (~447 MB)
```

**Via App Logs:**
Once deployed, check deploy logs for:
```
✅ RTAB-Map service initialized successfully with database: /data/database.db
```

---

### Step 7: Redeploy

After the database is uploaded:
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** (⟳ button)
3. Or push any small change to trigger redeploy

---

## 🧪 Verification Checklist

After successful deployment:

### 1. Check Deploy Logs
Look for these success messages:
```
✅ RTAB-Map service initialized successfully with database: /data/database.db
✅ All services initialized - API ready for requests
```

### 2. Test Health Endpoint
Open in browser:
```
https://store-navigator-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "rtabmap-api",
  "version": "1.1",
  "features": ["localization", "search-and-localize", "object-search"],
  "timestamp": 1731531234.56
}
```

### 3. Test Root Endpoint
```
https://store-navigator-production.up.railway.app/
```

Expected:
```json
{
  "service": "rtabmap-api",
  "status": "running",
  "version": "1.1"
}
```

### 4. Test from Frontend
Open on your phone:
```
https://kasrajb.github.io/store-navigator/
```

1. Select a product
2. Click "Localize Me"
3. Grant camera permission
4. Take a photo
5. Should see localization results!

---

## 🚨 Troubleshooting

### Build succeeds but deploy fails with "database not found"
✅ **Expected!** The database volume isn't attached or file isn't uploaded yet.
→ Complete Steps 3-5 above.

### "No such file or directory: /data/database.db"
❌ Database file isn't in the correct location.
→ Check volume mount path is `/data`
→ Check file is named `database.db` (not `corridor-V3.db`)

### Volume attached but app still can't find database
❌ Volume might not be properly mounted.
→ Ensure mount path is **exactly** `/data`
→ Check Railway logs for volume mount confirmation
→ Try redeploying after attaching volume

### Build fails with Docker errors
❌ Root directory might not be set.
→ Settings → Root Directory → `backend` → Save

---

## 📞 Need Help?

If you're stuck on the file upload:

1. **Railway Discord**: https://discord.gg/railway
2. **Railway Docs**: https://docs.railway.app/reference/volumes
3. **Alternative**: I can help you add a temporary upload endpoint to your app

---

## 💡 Quick Workaround for Testing

If you just want to test the deployment without the full database:

1. Create a minimal test database (smaller file)
2. Or modify `app.py` to work with a mock/dummy database
3. This lets you verify the rest of the deployment works

Let me know which approach you'd like to take!
