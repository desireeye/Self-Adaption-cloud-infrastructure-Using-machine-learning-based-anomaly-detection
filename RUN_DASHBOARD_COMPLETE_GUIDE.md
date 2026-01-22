# 🎨 COMPLETE DASHBOARD RUN GUIDE

## ⚡ Ultra-Quick Start (Copy & Paste)

### For Windows PowerShell:

**Terminal 1 - Backend:**
```powershell
$projectRoot = "C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
cd "$projectRoot\dashboard\backend"
python -m pip install --upgrade pip
pip install -r requirements_clean.txt --no-cache-dir
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```powershell
$projectRoot = "C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
cd "$projectRoot\dashboard\frontend"
npm install --legacy-peer-deps
npm start
```

Then open: **http://localhost:3000**

---

## 🔍 Complete Setup Steps

### Step 1: Ensure Main System Has Run

```bash
cd "C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
python main.py run --duration 60
```

This generates the data files that the dashboard will display.

### Step 2: Setup Backend (Terminal 1)

```bash
# Navigate to backend directory
cd "C:\Users\arzoo\OneDrive\Desktop\self-adaptive project\dashboard\backend"

# Upgrade pip (important!)
python -m pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements_clean.txt --no-cache-dir

# Start the FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Verify it works:**
```
Browser: http://localhost:8000/docs
```

### Step 3: Setup Frontend (Terminal 2)

```bash
# Navigate to frontend directory
cd "C:\Users\arzoo\OneDrive\Desktop\self-adaptive project\dashboard\frontend"

# Install Node dependencies
npm install --legacy-peer-deps

# Start development server
npm start
```

**Expected output:**
```
Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000
```

**Verify it works:**
```
Browser: http://localhost:3000
```

---

## 🛠️ Troubleshooting Installation Issues

### Problem 1: Python Dependencies Won't Install

**Solution A - Clear pip cache:**
```bash
pip cache purge
pip install -r requirements_clean.txt --no-cache-dir
```

**Solution B - Install one at a time:**
```bash
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install pydantic==2.5.0
pip install python-multipart==0.0.6
pip install psutil
pip install scikit-learn
pip install pandas
pip install numpy
```

**Solution C - Use system Python instead of virtual env:**
```bash
python -m pip install -r requirements_clean.txt
```

### Problem 2: npm Install Issues

**Solution A - Use legacy peer deps:**
```bash
npm install --legacy-peer-deps
```

**Solution B - Force install:**
```bash
npm install --force
```

**Solution C - Clear npm cache:**
```bash
npm cache clean --force
npm install
```

### Problem 3: Port Already in Use

**Backend (8000):**
```bash
netstat -ano | findstr :8000
# Kill process: taskkill /PID <PID> /F
# Or use different port: uvicorn main:app --port 8001
```

**Frontend (3000):**
```bash
netstat -ano | findstr :3000
# Kill process: taskkill /PID <PID> /F
# Or press 'Y' when prompted, or change port in .env
```

---

## ✅ Verification Checklist

### 1. Main System Data
```bash
# Check if data files exist
ls "C:\Users\arzoo\OneDrive\Desktop\self-adaptive project\data\"
```

Should show:
- `metrics_*.json` (latest run)
- `anomalies_*.json`
- `decisions_*.json`

### 2. Backend Running
```bash
# Check if server is responding
curl http://localhost:8000/docs
# or
Invoke-WebRequest http://localhost:8000/docs -UseBasicParsing
```

### 3. Frontend Running
```bash
# Check if dashboard is accessible
# Open in browser: http://localhost:3000
# Should show Bento-grid dashboard with metric cards
```

### 4. Integration Working
```bash
# Check if backend can read main system data
curl http://localhost:8000/api/health/data-availability
```

Should return JSON with status "connected".

---

## 📊 Dashboard Pages

Once running at http://localhost:3000:

1. **Home/Overview**
   - System status
   - Key metrics
   - Health score
   - Recent anomalies

2. **Metrics**
   - Real-time CPU, Memory, Disk
   - Network throughput
   - Historical trends
   - Charts and graphs

3. **Anomalies**
   - Anomaly timeline
   - Severity indicators
   - Anomaly details
   - Detection history

4. **Actions**
   - Recovery actions taken
   - Success rate
   - Action timeline
   - Impact analysis

5. **System**
   - Integration status
   - Data availability
   - Connection status
   - Configuration info

---

## 🔄 Development Workflow

### Making Changes

1. **Backend Changes:**
   - Edit files in `dashboard/backend/`
   - Server auto-reloads (due to `--reload` flag)
   - Check http://localhost:8000/docs for API changes

2. **Frontend Changes:**
   - Edit files in `dashboard/frontend/src/`
   - Browser auto-refreshes (hot reload)
   - Check http://localhost:3000 for UI changes

### Debugging

**Backend Debug Logs:**
```bash
# Check terminal output where backend is running
# Or view logs: tail -f logs/backend.log
```

**Frontend Debug Console:**
```bash
# Open browser DevTools: F12 or Ctrl+Shift+I
# Check Console tab for errors
# Check Network tab for API calls
```

**API Testing:**
```bash
# Use Swagger UI: http://localhost:8000/docs
# Or use curl:
curl http://localhost:8000/api/health/integrated-status
curl http://localhost:8000/api/health/system-summary
```

---

## 📝 Useful Commands

### View Main System Logs
```bash
cat "C:\Users\arzoo\OneDrive\Desktop\self-adaptive project\logs\system.log"
# Or tail for live logs:
Get-Content logs\system.log -Tail 20 -Wait
```

### View Latest Metrics
```bash
cd "C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
python -c "import json; data = json.load(open('data/metrics_*.json', 'r')); print(json.dumps(data[-1], indent=2))"
```

### Restart Services (from project root)
```bash
# Kill all Python processes (be careful!)
taskkill /F /IM python.exe

# Kill all Node processes
taskkill /F /IM node.exe
```

### Check Ports
```bash
# Windows: Check which ports are in use
netstat -ano | findstr "ESTABLISHED"

# Check specific port
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

---

## 🌐 Accessing from Other Machines

If you want to access the dashboard from another computer:

### Backend API
```
http://<YOUR_IP_ADDRESS>:8000
http://<YOUR_IP_ADDRESS>:8000/docs  # API documentation
```

### Frontend Dashboard
1. Edit `dashboard/frontend/.env`:
   ```
   REACT_APP_API_BASE_URL=http://<YOUR_IP_ADDRESS>:8000
   ```

2. Restart frontend: `npm start`

3. Access from other machine: `http://<YOUR_IP_ADDRESS>:3000`

### Find Your IP Address
```bash
ipconfig
# Look for "IPv4 Address"
```

---

## 🚀 Production Deployment

### Using Docker

**Create `Dockerfile` for backend:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY dashboard/backend .
RUN pip install -r requirements_clean.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t dashboard-backend .
docker run -p 8000:8000 dashboard-backend
```

### Using Systemd (Linux)

**Create service file:**
```bash
sudo nano /etc/systemd/system/dashboard.service
```

Content:
```
[Unit]
Description=Dashboard Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/dashboard/backend
ExecStart=/usr/bin/python -m uvicorn main:app --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable dashboard
sudo systemctl start dashboard
```

### Using PM2 (Node.js)

```bash
npm install -g pm2
pm2 start "npm start" --name dashboard-frontend
pm2 startup
pm2 save
```

---

## 📞 Support

### Verify Integration
```bash
python VERIFY_DASHBOARD_INTEGRATION.py
```

### Check System Health
```bash
curl http://localhost:8000/api/health/integrated-status
```

### View Connection Status
```bash
curl http://localhost:8000/api/health/data-availability
```

### Test API Endpoints
```bash
# System Summary
curl http://localhost:8000/api/health/system-summary

# Health Status
curl http://localhost:8000/api/health/status

# Metrics
curl http://localhost:8000/api/metrics/current
```

---

## 📚 Documentation

| Document | Location |
|----------|----------|
| **Quick Start** | `DASHBOARD_QUICK_START.md` |
| **Integration** | `dashboard/INTEGRATION_GUIDE.md` |
| **Architecture** | `docs/ARCHITECTURE.md` |
| **Full README** | `README.md` |
| **Deployment** | `docs/DEPLOYMENT.md` |

---

## 🎉 You're Ready!

```
1. ✅ Main system has run and generated data
2. ✅ Backend dependencies installed
3. ✅ Backend running on port 8000
4. ✅ Frontend running on port 3000
5. ✅ Dashboard displaying system status
6. ✅ Integration with main system complete
```

### Next Step
```bash
Open: http://localhost:3000
```

**Enjoy your beautiful, fully-integrated Self-Adaptive Cloud Infrastructure dashboard! 🎊**
