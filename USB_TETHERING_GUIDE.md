# 📱 iPhone USB Tethering Setup Guide
## Local Testing Without Cloud Deployment

This guide explains how to test the Store Navigator app on your iPhone using USB tethering to bypass network connectivity issues.

---

## ✅ Why USB Tethering?

**Problem:** Mobile hotspots have client isolation that prevents your phone from accessing services running on connected devices.

**Solution:** USB tethering creates a direct network bridge between your iPhone and PC, allowing your iPhone to access `localhost` as if services were running on the phone itself!

**Benefits:**
- ✅ No cloud deployment needed
- ✅ Bypasses hotspot client isolation completely
- ✅ Works with HTTP (camera access works via localhost)
- ✅ Faster than wireless (USB connection)
- ✅ Perfect for local development and testing

---

## 🚀 Quick Start (15 Minutes)

### Step 1: Install iPhone USB Drivers on Windows

**Option A: iTunes (Full Install)**
```powershell
winget install Apple.iTunes
```

**Option B: Apple Devices App (Lightweight - Windows 11 only)**
- Open Microsoft Store
- Search for "Apple Devices"
- Install the app

**Why?** Windows needs these drivers to recognize your iPhone as a network device.

---

### Step 2: Enable Personal Hotspot on iPhone

1. Open **Settings** app on iPhone
2. Tap **Personal Hotspot** (or **Cellular** > **Personal Hotspot**)
3. Toggle **Allow Others to Join** to ON
4. You'll see "To connect using USB..."

**Important:** Leave this screen open while you connect the cable.

---

### Step 3: Connect iPhone to PC via USB

1. Use your iPhone **charging cable** (Lightning or USB-C)
2. Connect iPhone to PC USB port
3. On iPhone: Tap **Trust** when prompted
4. On PC: Windows will install drivers automatically (takes 30-60 seconds)
5. You'll see a notification: "Apple iPhone - Network connection"

**Verify Connection:**
Open Command Prompt and type:
```powershell
ipconfig
```

Look for a new adapter like:
```
Ethernet adapter Ethernet 3:
   Description . . . . . . . . : Apple Mobile Device Ethernet
   IPv4 Address. . . . . . . . : 172.20.10.2
```

✅ If you see this, USB tethering is working!

---

### Step 4: Start Backend (Docker)

Open PowerShell in your backend directory:

```powershell
cd "C:\Users\kasra\Desktop\Kasra\Telegram\Fall 2025\ECSE 542 Milestone #3\store-navigator\backend"
docker-compose up -d
```

**Verify it's running:**
```powershell
docker ps
# Should show rtabmap-api container running on port 8040
```

**Test the backend:**
```powershell
curl http://localhost:8040/health
```

Expected response:
```json
{"status": "ok", "service": "rtabmap-api", ...}
```

---

### Step 5: Start Frontend (Python Web Server)

Open a NEW PowerShell window:

```powershell
cd "C:\Users\kasra\Desktop\Kasra\Telegram\Fall 2025\ECSE 542 Milestone #3\store-navigator"
python -m http.server 8080
```

You should see:
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

**Test the frontend on PC:**
Open browser to: http://localhost:8080
(Should show your Store Navigator app)

---

### Step 6: Test on iPhone! 📱

1. **Open Safari** on your iPhone (while still connected via USB)
2. Navigate to: **`http://localhost:8080`**
3. You should see the Store Navigator app load!

**Important:** Use `localhost`, NOT an IP address. USB tethering makes `localhost` work on your iPhone.

---

## 🧪 Testing the Camera Localization Feature

Once the app loads on your iPhone:

1. **Select a product** from the category list
   - Example: Navigate to "Dairy & Eggs" > "Milk"

2. **Click "Localize Me" button**
   - A camera interface should appear

3. **Grant camera permissions** when prompted
   - Safari will ask: "Allow localhost to access camera?"
   - Tap **Allow**

4. **Capture a photo**
   - Take a picture of your surroundings
   - The photo will be sent to the backend for localization

5. **View results**
   - You should see:
     - Your current position coordinates
     - Detected objects in the scene
     - Navigation guidance to your selected product
     - Distance and direction information

---

## ✅ Verification Checklist

### On PC (Before Testing on iPhone):

- [ ] iTunes or Apple Devices app installed
- [ ] Docker Desktop running
- [ ] Backend container running (`docker ps` shows rtabmap-api)
- [ ] Backend responds to: `http://localhost:8040/health`
- [ ] Frontend web server running on port 8080
- [ ] Frontend loads in PC browser: `http://localhost:8080`
- [ ] Windows Firewall allows Docker (should be configured already)

### On iPhone (With USB Connected):

- [ ] Personal Hotspot enabled
- [ ] iPhone connected via USB cable
- [ ] iPhone shows "Personal Hotspot: 1 Connection" (or similar)
- [ ] Safari can load: `http://localhost:8080`
- [ ] Camera permission granted to Safari/localhost
- [ ] "Localize Me" button appears and works
- [ ] Photos are uploaded and processed successfully

---

## 🔧 Troubleshooting

### Issue: iPhone not showing as network adapter

**Solutions:**
1. Try a different USB port (use USB 3.0 port if available)
2. Try a different USB cable (some cables are charge-only)
3. Restart iPhone
4. Uninstall and reinstall iTunes/Apple Devices app
5. Update Windows: Settings > Windows Update

### Issue: "Trust This Computer?" doesn't appear

**Solutions:**
1. Disconnect cable
2. On iPhone: Settings > General > Reset > Reset Location & Privacy
3. Reconnect cable
4. "Trust" prompt should appear again

### Issue: Safari on iPhone shows "Cannot connect to localhost"

**Check:**
1. Is Personal Hotspot still enabled on iPhone?
2. Is the USB cable still connected?
3. Run `ipconfig` on PC - do you see the Apple network adapter?
4. Can you access http://localhost:8080 from PC browser?

**Fix:**
1. Disconnect and reconnect USB cable
2. Toggle Personal Hotspot off and back on
3. Restart both services (backend and frontend)

### Issue: Camera permission denied

**Solutions:**
1. Safari Settings on iPhone > Camera > Allow for localhost
2. Settings > Safari > Camera > Allow
3. Try accessing via `http://127.0.0.1:8080` instead of `localhost`

### Issue: Backend returns "Failed to process image" or 500 errors

**Check:**
1. Docker logs: `docker logs rtabmap-api --tail 50`
2. Is the database file present? Check backend logs for "database not found"
3. Is test image directory mounted correctly?

**Verify database:**
```powershell
docker exec -it rtabmap-api ls -lh /data/
# Should show database.db (~447 MB)
```

### Issue: Frontend loads but "Localize Me" button doesn't appear

**Check:**
1. Open Safari Developer Tools (if available)
2. Check console for JavaScript errors
3. Verify API_CONFIG.BASE_URL in script.js is `http://localhost:8040`
4. Test backend manually: `curl http://localhost:8040/`

---

## 📊 Performance Tips

### Keep iPhone Plugged In
- USB tethering uses more battery
- Keep iPhone charging while testing

### Monitor Backend Performance
```powershell
# Check CPU/Memory usage
docker stats rtabmap-api

# View real-time logs
docker logs -f rtabmap-api
```

### Test Image Size
- Keep test photos under 5 MB for faster processing
- Backend processes images in ~7-10 seconds typically

---

## 🎓 For Milestone 3 Pilot Study

### Documentation to Include:

1. **Setup Method:** 
   "Tested using iPhone USB tethering to Windows PC running Docker containers"

2. **Network Configuration:**
   - Frontend: Python HTTP server (localhost:8080)
   - Backend: Docker container (localhost:8040)
   - Connection: USB tethering (Personal Hotspot via cable)

3. **Testing Environment:**
   - Device: iPhone [model] with iOS [version]
   - Browser: Safari [version]
   - PC: Windows 11 with Docker Desktop

4. **Success Metrics:**
   - Camera access: ✅ Works via localhost
   - Image upload: ✅ Successful
   - Localization processing time: ~7-10 seconds
   - Navigation guidance: ✅ Displayed correctly

### Taking Screenshots for Report:

1. **Setup photos:**
   - iPhone connected via USB with Personal Hotspot screen visible
   - PC terminal showing backend/frontend running

2. **App screenshots:**
   - Safari on iPhone showing the app at localhost:8080
   - Camera permission prompt
   - Camera capture interface
   - Localization results display

3. **Technical proof:**
   - `ipconfig` output showing Apple network adapter
   - Docker containers running (`docker ps`)
   - Backend logs showing successful localization

---

## 📝 Commands Quick Reference

```powershell
# Check iPhone connection
ipconfig | findstr "Apple"

# Start backend
cd backend
docker-compose up -d

# Check backend health
curl http://localhost:8040/health

# Start frontend
cd ..
python -m http.server 8080

# View backend logs
docker logs -f rtabmap-api

# Stop services
docker-compose down
# Press Ctrl+C to stop web server
```

---

## 🔄 Alternative: Shared WiFi Network

If USB tethering doesn't work for any reason:

1. Connect both iPhone and PC to the **same WiFi network**
   - McGill WiFi, home WiFi, coffee shop WiFi, etc.

2. Find PC's IP on that network:
   ```powershell
   ipconfig
   # Look for "Wireless LAN adapter Wi-Fi"
   ```

3. Update `script.js`:
   ```javascript
   BASE_URL: 'http://[PC-IP]:8040'  // e.g., 'http://192.168.1.100:8040'
   ```

4. On iPhone Safari: `http://[PC-IP]:8080`

**Note:** You'll still need to allow camera access, which might be restricted on non-localhost HTTP pages depending on iOS version.

---

## 📞 Need Help?

If you encounter issues not covered here:

1. Check Docker logs: `docker logs rtabmap-api --tail 100`
2. Check Windows Event Viewer for USB connection errors
3. Verify firewall rules are still in place for ports 8040/8080
4. Try the shared WiFi alternative method

---

## ✨ Success!

Once everything works, you should be able to:
- ✅ Open the app on your iPhone via USB tethering
- ✅ Use your iPhone camera to capture photos
- ✅ Get real-time localization and navigation guidance
- ✅ Complete your Milestone 3 pilot study locally!

Good luck with your pilot study! 🚀
