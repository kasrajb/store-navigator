# 📱 iPhone Personal Hotspot Setup Guide
## Local Testing - PC Connected to iPhone Hotspot

This guide explains how to test the Store Navigator app when your PC is connected to your iPhone's Personal Hotspot.

---

## ✅ Why This Method?

**Setup:** PC connects to iPhone's wireless hotspot, phone accesses services via PC's IP address.

**Benefits:**
- ✅ No USB cable needed
- ✅ No iTunes installation required
- ✅ Simple wireless connection
- ✅ Works great if hotspot allows device communication

**Potential Issue:**
- ⚠️ Some mobile hotspots have "client isolation" enabled, preventing the iPhone from accessing devices connected to its own hotspot
- If this happens, you'll need USB tethering or shared WiFi instead

---

## 🚀 Quick Start (10 Minutes)

### Step 1: Enable Personal Hotspot on iPhone (2 minutes)

1. Open **Settings** app on iPhone
2. Tap **Personal Hotspot** (or **Cellular** > **Personal Hotspot**)
3. Toggle **Allow Others to Join** to **ON**
4. Note the WiFi password shown on this screen

---

### Step 2: Connect PC to iPhone Hotspot (2 minutes)

**On Windows PC:**

1. Click WiFi icon in system tray (bottom right)
2. Look for your iPhone's hotspot name (usually "iPhone" or your name)
3. Click on it and select **Connect**
4. Enter the WiFi password from your iPhone
5. Wait for connection to establish

**Verify Connection:**
Open PowerShell and run:
```powershell
ipconfig
```

Look for **Wireless LAN adapter Wi-Fi** section:
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 172.20.10.2
   Subnet Mask . . . . . . . . . . . : 255.255.255.240
   Default Gateway . . . . . . . . . : 172.20.10.1
```

✅ Your PC's IP is: **172.20.10.2**
✅ iPhone's IP (gateway) is: **172.20.10.1**

---

### Step 3: Ensure Windows Firewall Allows Connections (1 minute)

You should already have firewall rules from earlier setup. Verify:

```powershell
# Check if rules exist
netsh advfirewall firewall show rule name="Backend API (8040)" dir=in
netsh advfirewall firewall show rule name="Frontend Web Server (8080)" dir=in
```

If rules don't exist, add them:
```powershell
# Run as Administrator
netsh advfirewall firewall add rule name="Backend API (8040)" dir=in action=allow protocol=TCP localport=8040
netsh advfirewall firewall add rule name="Frontend Web Server (8080)" dir=in action=allow protocol=TCP localport=8080
```

---

### Step 4: Start Backend (Docker) (2 minutes)

```powershell
cd "C:\Users\kasra\Desktop\Kasra\Telegram\Fall 2025\ECSE 542 Milestone #3\store-navigator\backend"
docker-compose up -d
```

**Verify it's running:**
```powershell
# Check containers
docker ps

# Test backend from PC
curl http://localhost:8040/health

# Test backend using PC's IP (what iPhone will use)
curl http://172.20.10.2:8040/health
```

Expected response:
```json
{"status": "ok", "service": "rtabmap-api", ...}
```

---

### Step 5: Start Frontend Web Server (1 minute)

Open a **NEW PowerShell window**:

```powershell
cd "C:\Users\kasra\Desktop\Kasra\Telegram\Fall 2025\ECSE 542 Milestone #3\store-navigator"
python -m http.server 8080
```

**Verify it's running:**

On PC, open browser to:
- `http://localhost:8080` ✅ Should load the app
- `http://172.20.10.2:8080` ✅ Should also load (this is what iPhone will use)

---

### Step 6: Test on iPhone! 📱 (2 minutes)

1. **On iPhone**, open **Safari**
2. Navigate to: **`http://172.20.10.2:8080`**
3. The Store Navigator app should load!

⚠️ **If it doesn't load:**
This means your iPhone hotspot has client isolation enabled. See troubleshooting section below.

---

### Step 7: Test Camera Localization 📸 (5 minutes)

⚠️ **Important Camera Access Note:**

Mobile Safari restricts camera access to:
- ✅ HTTPS sites (secure)
- ✅ localhost
- ❌ HTTP with IP addresses (like http://172.20.10.2:8080)

**This means camera access may not work with this setup!**

**Workaround options:**
1. **USB Tethering** - Use localhost instead of IP (see USB_TETHERING_GUIDE.md)
2. **Self-Signed Certificate** - Set up HTTPS (complex)
3. **File Upload** - Manually select photos instead of live camera (limited testing)

If camera works (depends on iOS version):
1. Select a product category
2. Click **"Localize Me"** button
3. Grant camera permission
4. Take a photo
5. Wait for localization results

---

## ✅ Verification Checklist

### On PC (Before Testing on iPhone):

- [ ] PC connected to iPhone's Personal Hotspot
- [ ] PC IP confirmed as 172.20.10.2 (`ipconfig`)
- [ ] Windows Firewall rules added for ports 8040 and 8080
- [ ] Docker Desktop running
- [ ] Backend container running (`docker ps`)
- [ ] Backend responds: `curl http://172.20.10.2:8040/health`
- [ ] Frontend web server running on port 8080
- [ ] Frontend loads in PC browser: `http://172.20.10.2:8080`

### On iPhone:

- [ ] Connected to Personal Hotspot (stays connected when you use it)
- [ ] Safari can load: `http://172.20.10.2:8080`
- [ ] App interface displays correctly
- [ ] Can navigate through categories

---

## 🔧 Troubleshooting

### Issue: iPhone can't access http://172.20.10.2:8080

**Cause:** iPhone hotspot has **client isolation** enabled (most do by default).

**What is client isolation?**
Security feature that prevents devices connected to the hotspot from talking to each other. The iPhone can't access its own connected devices.

**Solutions:**

**Option A: Use USB Tethering Instead (Recommended)**
See [USB_TETHERING_GUIDE.md](USB_TETHERING_GUIDE.md)
- Connect iPhone to PC via USB
- iPhone accesses via `http://localhost:8080` (works!)
- Camera access works on localhost

**Option B: Use Shared WiFi Network**
1. Disconnect from hotspot
2. Connect both PC and iPhone to the same WiFi network (home, McGill, coffee shop)
3. Find PC's new IP: `ipconfig` (look for Wi-Fi adapter)
4. Update script.js with new IP
5. Access from iPhone: `http://[new-PC-IP]:8080`
6. ⚠️ Camera may still not work due to HTTP (see Option A)

**Option C: PC as Hotspot**
1. Windows Settings > Network & Internet > Mobile hotspot
2. Turn ON "Share my Internet connection"
3. Connect iPhone to PC's hotspot
4. Find PC's IP in the hotspot network
5. Update script.js
6. Test from iPhone

### Issue: App loads but camera doesn't work

**Cause:** Mobile Safari restricts camera access on HTTP sites (non-localhost).

**Solutions:**
1. **Best:** Use USB tethering so iPhone accesses via localhost
2. **Alternative:** Use file upload instead of live camera (limited functionality)
3. **Complex:** Set up self-signed HTTPS certificate on PC

### Issue: Connection timeout when accessing backend

**Check:**
1. Is Docker container still running? `docker ps`
2. Is backend responding? `curl http://172.20.10.2:8040/health`
3. Are firewall rules in place? See Step 3
4. Is PC still connected to iPhone hotspot? Check WiFi connection

### Issue: Backend returns CORS errors

**Check backend logs:**
```powershell
docker logs rtabmap-api --tail 50
```

CORS should allow all origins for local testing. If not, check app.py configuration.

### Issue: "Cannot GET /" error

**Cause:** Web server not running or wrong port

**Fix:**
1. Ensure Python web server is running: `python -m http.server 8080`
2. Check it's serving from the correct directory (should have index.html)

---

## 📊 Network Diagram

```
┌─────────────────┐
│  iPhone Hotspot │ (172.20.10.1)
│   (Gateway)     │
└────────┬────────┘
         │ WiFi
         │
┌────────▼────────┐
│   Windows PC    │ (172.20.10.2)
│                 │
│  ┌───────────┐  │
│  │  Backend  │  │ Port 8040 → RTAB-Map API
│  │  (Docker) │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Frontend  │  │ Port 8080 → Web Server
│  │  (HTTP)   │  │
│  └───────────┘  │
└─────────────────┘
         │
         │ WiFi (if no client isolation)
         ▼
┌─────────────────┐
│ iPhone Safari   │
│ 172.20.10.2:8080│ ← Tries to access PC
└─────────────────┘
```

---

## 📝 Commands Quick Reference

```powershell
# Check PC IP on hotspot
ipconfig | findstr "172.20"

# Verify firewall rules
netsh advfirewall firewall show rule name="Backend API (8040)" dir=in
netsh advfirewall firewall show rule name="Frontend Web Server (8080)" dir=in

# Start backend
cd backend
docker-compose up -d

# Test backend (both ways)
curl http://localhost:8040/health
curl http://172.20.10.2:8040/health

# Start frontend (new window)
cd ..
python -m http.server 8080

# View backend logs
docker logs -f rtabmap-api

# Stop services
docker-compose down
# Ctrl+C to stop web server
```

---

## 🎓 For Milestone 3 Documentation

### If This Method Works:

**Testing Environment:**
- Network: PC connected to iPhone Personal Hotspot (wireless)
- PC IP: 172.20.10.2
- Backend: Docker container on port 8040
- Frontend: Python HTTP server on port 8080
- Access: iPhone Safari via `http://172.20.10.2:8080`

**Limitations:**
- Camera access may be restricted on HTTP with IP addresses
- Dependent on hotspot not having client isolation

### If This Method Doesn't Work (Client Isolation):

Document that you switched to USB tethering method (see USB_TETHERING_GUIDE.md) to bypass hotspot client isolation and enable camera access.

---

## ⚠️ Camera Access - Important Notes

### Mobile Safari Camera Restrictions:

Safari on iOS restricts `getUserMedia()` (camera access) to:
✅ **HTTPS sites** (secure connection)
✅ **localhost** (trusted local)
❌ **HTTP with IP address** (not trusted)

### This means:

With hotspot method (`http://172.20.10.2:8080`):
- ❌ Camera access will likely be **BLOCKED**
- ✅ Manual file upload might work (select existing photos)
- ✅ Navigation and UI features work fine

With USB tethering (`http://localhost:8080`):
- ✅ Camera access **WORKS**
- ✅ Full functionality including live capture

### Recommendation:

Use this hotspot method to:
- ✅ Test the app interface and navigation
- ✅ Test with pre-captured photos (file upload)
- ✅ Verify backend connectivity

Then switch to USB tethering for:
- ✅ Live camera capture testing
- ✅ Real-time localization demo
- ✅ Full pilot study functionality

---

## 🔄 Switch to USB Tethering

If you hit the camera access issue or client isolation, switch to USB method:

1. See full guide: [USB_TETHERING_GUIDE.md](USB_TETHERING_GUIDE.md)
2. Quick switch:
   - Connect iPhone to PC via USB
   - Update script.js: `BASE_URL: 'http://localhost:8040'`
   - Access from iPhone: `http://localhost:8080`
   - Camera will work!

---

## ✨ Success Indicators

### App loads and basic features work:
- ✅ Categories display correctly
- ✅ Navigation between screens works
- ✅ Product selection works
- ✅ "Localize Me" button appears

### Backend connectivity works:
- ✅ No CORS errors in Safari console
- ✅ API calls don't timeout
- ✅ Backend logs show requests received

### Camera might work (if lucky):
- ✅ Camera permission prompt appears
- ✅ Live camera feed displays
- ✅ Photo capture works
- ✅ Localization results display

If camera doesn't work due to HTTP/IP restrictions, proceed with USB tethering! 📱🔌
