# Bento Dashboard - Quick Setup & Run Guide

## ⏱️ 10-Minute Quick Start

### Prerequisites
- Python 3.8+ installed
- Node.js 14+ installed (for frontend, optional)
- Internet connection

### Step 1: Setup Backend (3 minutes)

```bash
cd dashboard/backend
pip install -r requirements.txt
python main.py
```

✅ Backend running at `http://localhost:8000`

### Step 2: Test Backend (1 minute)

Open browser and go to:
```
http://localhost:8000/docs
```

You'll see interactive API documentation with all endpoints.

### Step 3: Setup Frontend (3 minutes)

Open NEW terminal window:

```bash
cd dashboard/frontend
npm install
npm start
```

✅ Frontend running at `http://localhost:3000`

### Step 4: View Dashboard (1 minute)

Open browser and go to:
```
http://localhost:3000
```

🎉 Dashboard is live!

---

## 📊 What You'll See

### Metric Cards (Real-Time)
- **CPU Usage**: Live CPU percentage (0-100%)
- **Memory Usage**: RAM utilization
- **Disk Usage**: Storage usage
- **Network**: Network throughput (MB/s)
- **Anomaly Status**: NORMAL / WARNING / CRITICAL

### Charts
- **System Metrics Timeline**: 5-minute history of CPU, Memory, Disk
- **Anomaly Score Distribution**: Histogram showing anomaly distribution
- **Network Chart**: Upload/Download throughput

### Health Section
- **Health Gauge**: 0-100 score visualization
- **System Status**: STABLE / ADAPTING / RECOVERING
- **Recent Actions**: Timeline of executed adaptive actions

### Quick Actions
- **Scale Up**: Add resources
- **Scale Down**: Remove resources
- **Clear Cache**: Free memory
- **Optimize CPU**: Improve scheduling

---

## 🧪 Testing Endpoints

### Test Current Metrics
```bash
curl http://localhost:8000/api/metrics/current
```

Expected output:
```json
{
  "timestamp": "2026-01-21T10:30:00Z",
  "cpu_percent": 45.2,
  "memory_percent": 62.8,
  "disk_percent": 78.5,
  "network_bytes_sent": 1024000,
  "network_bytes_recv": 2048000,
  "temperature": 62.5
}
```

### Test Anomaly Detection
```bash
curl http://localhost:8000/api/anomalies/detect
```

Expected output:
```json
{
  "timestamp": "2026-01-21T10:30:00Z",
  "is_anomaly": false,
  "anomaly_score": 0.25,
  "anomaly_level": "normal",
  "confidence": 0.92,
  "affected_metrics": [],
  "feature_importances": {...}
}
```

### Test System Health
```bash
curl http://localhost:8000/api/health/status
```

### Trigger Action
```bash
curl -X POST "http://localhost:8000/api/health/trigger-action?action_type=scale_up&target=compute&reason=Test"
```

---

## 🔧 Troubleshooting

### "Port 8000 already in use"
```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port - edit main.py:
# uvicorn.run(app, host="0.0.0.0", port=8001)
```

### "Port 3000 already in use"
```bash
# Use different port
PORT=3001 npm start
```

### "CORS error in browser console"
- Ensure backend is running
- Verify API URL in frontend .env is correct
- Default: `REACT_APP_API_URL=http://localhost:8000`

### "Dashboard shows 'No Data'"
1. Check backend: `curl http://localhost:8000/health`
2. Check API: `curl http://localhost:8000/api/metrics/current`
3. Check browser console (F12) for errors
4. Verify both services running

### Dependencies not installing
```bash
# Clear cache
pip cache purge
npm cache clean --force

# Reinstall
pip install -r requirements.txt
npm install
```

---

## 📁 Project Structure

```
dashboard/
├── backend/                    # FastAPI server
│   ├── main.py                # Entry point
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── metrics.py    # Metrics endpoints
│   │   │   ├── anomalies.py  # Anomaly detection
│   │   │   └── health.py     # Health & actions
│   │   ├── models/           # Data models (Pydantic)
│   │   └── services/         # Business logic
│   │       ├── metrics_service.py
│   │       ├── anomaly_service.py
│   │       └── action_service.py
│   └── requirements.txt
│
└── frontend/                   # React app
    ├── public/
    │   └── index.html         # HTML template
    ├── src/
    │   ├── components/        # React components
    │   │   ├── MetricCards.jsx
    │   │   └── Charts.jsx
    │   ├── hooks/            # Custom hooks
    │   │   └── useApi.js     # API integration
    │   ├── pages/
    │   │   └── Dashboard.jsx  # Main page
    │   ├── styles/           # Tailwind CSS
    │   ├── App.jsx           # Root component
    │   └── index.jsx         # Entry point
    ├── package.json
    └── tailwind.config.js
```

---

## 🚀 Next Steps

### Option 1: Deploy Locally (Current)
✅ You're done! Dashboard is running.

### Option 2: Build Production Version
```bash
cd frontend
npm run build
# Creates 'build/' folder ready for hosting
```

### Option 3: Deploy to Cloud

**AWS:**
- Backend: EC2 + Gunicorn
- Frontend: S3 + CloudFront
- See INTEGRATION_GUIDE.md for details

**Azure:**
- Backend: App Service
- Frontend: Static Web Apps
- See INTEGRATION_GUIDE.md for details

**GCP:**
- Backend: Cloud Run
- Frontend: Cloud Storage + CDN
- See INTEGRATION_GUIDE.md for details

### Option 4: Docker Deployment
```bash
# From project root
docker-compose up
```

---

## 📚 Documentation

- **INTEGRATION_GUIDE.md** - Complete architecture & API specs
- **backend/README.md** - Backend setup & configuration
- **frontend/README.md** - Frontend setup & customization
- **API Docs** - http://localhost:8000/docs (interactive)

---

## ✅ Verification Checklist

- [ ] Backend started without errors
- [ ] Frontend started without errors
- [ ] Can access dashboard at http://localhost:3000
- [ ] Metric cards showing real data (not 0)
- [ ] Charts rendering and updating
- [ ] Status badge shows (STABLE/ADAPTING/etc)
- [ ] Can trigger actions (buttons working)
- [ ] No console errors (F12)
- [ ] Real-time updates (watch values change)

---

## 🎯 Key Features Demonstrated

✅ **Real-Time Monitoring** - CPU, Memory, Disk, Network in real-time  
✅ **ML Anomaly Detection** - Isolation Forest with 20 engineered features  
✅ **Adaptive Actions** - Auto-trigger recovery when anomalies detected  
✅ **Beautiful UI** - Bento-grid layout with dark theme  
✅ **Interactive Charts** - Recharts with real data  
✅ **API Integration** - Clean FastAPI backend  
✅ **Production Ready** - Error handling, logging, scalable  
✅ **Cloud Ready** - Deployable to AWS/Azure/GCP  

---

## 🆘 Getting Help

1. Check browser console (F12) for errors
2. Check backend logs in terminal
3. Review API response: http://localhost:8000/docs
4. Test endpoints with curl
5. Verify .env variables if using them

---

**Dashboard v1.0.0** | Ready to use!

Questions? Check INTEGRATION_GUIDE.md for detailed architecture and troubleshooting.
