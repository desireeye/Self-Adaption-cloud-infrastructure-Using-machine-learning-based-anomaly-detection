# 🚀 Dashboard Quick Start Guide

## Overview

The Bento Dashboard is fully integrated with the Self-Adaptive Cloud Infrastructure system. It provides real-time monitoring, anomaly detection visualization, and system health status.

## ✅ Prerequisites

- Python 3.8+ with pip
- Node.js 14+ with npm
- Main system already executed at least once (creates data files)

## 📋 Quick Setup (5 minutes)

### Step 1: Ensure Main System Has Run

First, run the main system to generate metrics data:

```bash
cd c:\Users\arzoo\OneDrive\Desktop\self-adaptive project
python main.py run --duration 60
```

This creates data files that the dashboard will display.

### Step 2: Start Backend API Server

**Option A - PowerShell Script (Easiest)**:
```powershell
cd c:\Users\arzoo\OneDrive\Desktop\self-adaptive project
.\RUN_DASHBOARD.ps1 -BackendOnly
```

**Option B - Manual Start**:
```bash
cd c:\Users\arzoo\OneDrive\Desktop\self-adaptive project\dashboard\backend

# Install dependencies (first time only)
pip install -r requirements_clean.txt

# Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ **Backend Ready**: http://localhost:8000/docs

### Step 3: Start Frontend Dashboard (New Terminal)

**Option A - PowerShell Script**:
```powershell
cd c:\Users\arzoo\OneDrive\Desktop\self-adaptive project
.\RUN_DASHBOARD.ps1 -FrontendOnly
```

**Option B - Manual Start**:
```bash
cd c:\Users\arzoo\OneDrive\Desktop\self-adaptive project\dashboard\frontend

# Install dependencies (first time only)
npm install

# Start development server
npm start
```

Expected output:
```
On Your Network:  http://192.168.x.x:3000
Local:            http://localhost:3000
```

✅ **Frontend Ready**: http://localhost:3000

## 🎨 Dashboard Features

### Real-Time Metrics
- CPU Usage (%)
- Memory Usage (%)
- Disk Usage (%)
- Network Throughput (MB/s)
- System Temperature (°C)

### Anomaly Detection
- ML-based anomaly detection results
- Anomaly timeline visualization
- Severity indicators (Normal/Warning/Critical)
- Historical anomaly records

### System Health
- Overall health score (0-100)
- Component-wise health assessment
- Adaptive engine status
- Recovery action history

### Integration with Main System
- Real-time data from system metrics
- ML anomaly detection results
- Adaptive decision logs
- Recovery action tracking

## 🔗 API Endpoints

### Integrated System Endpoints

**System Summary** (Complete overview):
```
GET /api/health/system-summary
```

**Integrated Status** (Combined health):
```
GET /api/health/integrated-status
```

**Data Availability** (System connection check):
```
GET /api/health/data-availability
```

### Standard Endpoints

**Metrics**:
```
GET /api/metrics/current
GET /api/metrics/history?limit=100
GET /api/metrics/statistics
```

**Anomalies**:
```
GET /api/anomalies/current
GET /api/anomalies/history?limit=50
GET /api/anomalies/statistics
```

**Health**:
```
GET /api/health/status
GET /api/health/actions
GET /api/health/actions/statistics
```

### API Documentation

Interactive API documentation available at:
```
http://localhost:8000/docs
```

## 🔧 Configuration

### Backend Configuration

Edit `dashboard/backend/main.py` to configure:

- **CORS Origins**: Allow specific frontend domains
- **Log Level**: Set to DEBUG for detailed logging
- **API Port**: Change from 8000 to another port

### Frontend Configuration

Edit `dashboard/frontend/.env` (create if needed):

```
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=5000
REACT_APP_AUTO_REFRESH=true
REACT_APP_REFRESH_INTERVAL=3000
```

## 📊 Dashboard Views

### 1. Home/Overview
- System status at a glance
- Key metrics dashboard
- Recent anomalies
- Health score gauge

### 2. Metrics
- Real-time metric charts
- Historical trends
- Comparative analysis
- Peak/average/min values

### 3. Anomalies
- Anomaly detection timeline
- Severity distribution
- Anomaly details
- False positive tracking

### 4. Actions
- Recent recovery actions
- Action success rate
- Timeline of adaptations
- Resource impact analysis

### 5. System
- Integration status
- Data availability
- System connectivity
- Configuration info

## ✅ Verification Steps

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health/status
```

Should return:
```json
{
  "status": "stable",
  "health_score": 85.5,
  "timestamp": "2026-01-21T18:00:00"
}
```

### 2. Check Data Integration

```bash
curl http://localhost:8000/api/health/data-availability
```

Should return connection status and available data files.

### 3. Check Frontend

Open browser and navigate to:
```
http://localhost:3000
```

Should show:
- Dashboard loading
- Metric cards with data
- Charts with historical data
- System health gauge

## 🐛 Troubleshooting

### Issue: "Cannot connect to backend"

**Solution**:
1. Verify backend is running: `http://localhost:8000/docs`
2. Check CORS configuration in `dashboard/backend/main.py`
3. Verify both services are on same machine or network

### Issue: "No data available"

**Solution**:
1. Run main system first: `python main.py run --duration 60`
2. Check data files exist in `data/` folder
3. Verify integration paths in `dashboard/backend/app/services/system_integration.py`

### Issue: "npm install fails"

**Solution**:
```bash
npm install --legacy-peer-deps
# Or
npm install --force
```

### Issue: "Python dependencies error"

**Solution**:
```bash
pip install --upgrade pip
pip install -r requirements_clean.txt --no-cache-dir
```

## 🚀 Production Deployment

### Docker Support (Coming Soon)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY dashboard/backend .
RUN pip install -r requirements_clean.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Environment Variables

Create `.env` file in `dashboard/backend/`:
```
PROJECT_ROOT=/path/to/self-adaptive project
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
DATABASE_URL=sqlite:///./dashboard.db
```

## 📈 Performance Tips

1. **Limit History**: Reduce API history limits for faster loads
2. **Caching**: Enable Redis caching for frequently accessed data
3. **Pagination**: Use pagination for large datasets
4. **Compression**: Enable gzip in Uvicorn config

## 🔐 Security (Production)

1. **CORS**: Restrict to specific origins
2. **Authentication**: Add JWT tokens
3. **HTTPS**: Use SSL certificates
4. **Rate Limiting**: Add API rate limiting
5. **Data Validation**: Strict input validation

## 📝 Logs

### Backend Logs
```bash
# View live logs
tail -f logs/backend.log

# Search for errors
grep ERROR logs/backend.log
```

### Frontend Logs
Open browser DevTools (F12) and check Console tab.

## 🆘 Support

For issues or questions:

1. Check `dashboard/README.md` for detailed documentation
2. Review `dashboard/INTEGRATION_GUIDE.md` for architecture
3. Check logs in `logs/` directory
4. Verify main system is running correctly

## 📚 Additional Resources

- **Main README**: `c:\Users\arzoo\OneDrive\Desktop\self-adaptive project\README.md`
- **Architecture Docs**: `docs/ARCHITECTURE.md`
- **Integration Guide**: `dashboard/INTEGRATION_GUIDE.md`
- **API Reference**: `http://localhost:8000/docs` (when backend running)

## ✨ Next Steps

1. ✅ Start both backend and frontend services
2. ✅ Access dashboard at http://localhost:3000
3. ✅ Verify system data is displayed
4. ✅ Review metrics and anomalies
5. ✅ Monitor recovery actions
6. ✅ Customize dashboard theme/colors if desired

---

**Status**: ✅ **DASHBOARD READY AND FULLY INTEGRATED**

The dashboard is production-ready and fully integrated with the main Self-Adaptive System!
