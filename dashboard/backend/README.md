# Self-Adaptive Dashboard Backend Setup Guide

## 📋 Prerequisites

- Python 3.8+
- pip or conda
- Windows PowerShell / macOS/Linux bash

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd dashboard/backend
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 3. Access API Documentation
Open your browser and navigate to:
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 📊 API Endpoints

### Metrics
- `GET /api/metrics/current` - Get current system metrics
- `GET /api/metrics/history?seconds=300` - Get metrics history
- `GET /api/metrics/statistics?seconds=300` - Get metrics statistics
- `GET /api/metrics/full-history` - Get all stored metrics

### Anomalies
- `GET /api/anomalies/detect` - Detect anomalies in current metrics
- `GET /api/anomalies/model-stats` - Get ML model statistics
- `GET /api/anomalies/retrain` - Manually trigger model retraining
- `GET /api/anomalies/summary?hours=1` - Get anomaly summary

### Health & Actions
- `GET /api/health/status` - Get overall system health
- `POST /api/health/trigger-action` - Trigger adaptive action
- `GET /api/health/actions/history?limit=100` - Get action history
- `GET /api/health/actions/active` - Get active actions
- `GET /api/health/actions/statistics` - Get action statistics

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file in the backend directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Metrics Collection
METRICS_COLLECTION_INTERVAL=1
METRICS_MAX_HISTORY=3600

# Anomaly Detection
ANOMALY_DETECTION_ENABLED=True
ANOMALY_DETECTION_CONTAMINATION=0.05
ANOMALY_DETECTION_N_ESTIMATORS=100

# Model Retraining
MODEL_RETRAIN_INTERVAL=3600
MODEL_MIN_SAMPLES=50
```

### Configuration in Code
Edit `app/models/metrics.py` and `app/services/*.py` for advanced configuration.

## 🧪 Testing Endpoints

### Test Metrics Endpoint
```bash
curl http://localhost:8000/api/metrics/current
```

### Test Anomaly Detection
```bash
curl http://localhost:8000/api/anomalies/detect
```

### Test Health Status
```bash
curl http://localhost:8000/api/health/status
```

### Trigger Action
```bash
curl -X POST "http://localhost:8000/api/health/trigger-action?action_type=scale_up&target=compute&reason=Testing"
```

## 📈 ML Model Integration

The backend integrates with your main project's ML components:

### Automatic Integration
- **Metrics Collection**: Uses `psutil` for real-time metrics
- **Anomaly Detection**: Integrates with `src/anomaly_detection/anomaly_detector.py`
- **Data Preprocessing**: Uses `src/preprocessing/data_preprocessor.py`
- **Recovery Actions**: Integrates with `src/recovery_actions/recovery_executor.py`

### Manual Model Training
```python
from app.services.anomaly_service import get_anomaly_service

service = get_anomaly_service()
service.retrain_model()
```

## 🚀 Production Deployment

### Docker
```bash
# Build Docker image
docker build -t dashboard-backend .

# Run container
docker run -p 8000:8000 dashboard-backend
```

### AWS EC2
```bash
# Install Python
sudo yum install python3 python3-pip

# Clone/upload code
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn for production
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Azure VM
Similar to AWS - install Python, dependencies, and run with Gunicorn/systemd.

### GCP Compute Engine
```bash
# Install dependencies
pip install -r requirements.txt

# Run as systemd service for persistence
```

## 🔍 Monitoring & Logs

Logs are written to console by default. To enable file logging:

```python
# Edit main.py
import logging

logging.basicConfig(
    filename='logs/dashboard.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Change port in main.py
uvicorn.run(app, host="0.0.0.0", port=8001)

# Or kill existing process
lsof -i :8000  # Find process
kill -9 <PID>   # Kill process
```

### ML Module Import Errors
Ensure parent project is in `PYTHONPATH`:
```bash
export PYTHONPATH="${PYTHONPATH}:../"
python main.py
```

### No Metrics Data
1. Check `/api/metrics/current` returns data
2. Verify `psutil` can access system metrics
3. Check user has permission to read /proc (Linux)

## 📚 API Response Examples

### Current Metrics Response
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

### Anomaly Detection Response
```json
{
  "timestamp": "2026-01-21T10:30:00Z",
  "is_anomaly": false,
  "anomaly_score": 0.25,
  "anomaly_level": "normal",
  "confidence": 0.92,
  "affected_metrics": [],
  "feature_importances": {"cpu": 0.15, "memory": 0.08, "disk": 0.02}
}
```

### Health Status Response
```json
{
  "timestamp": "2026-01-21T10:30:00Z",
  "status": "stable",
  "health_score": 85.5,
  "metrics": {...},
  "last_anomaly_detected": null,
  "anomalies_in_last_hour": 0,
  "active_adaptations": 0,
  "recent_actions": []
}
```

## 🔐 Security Considerations

For production deployments:

1. **API Authentication**: Add API keys
   ```python
   from fastapi import Depends, HTTPException
   from fastapi.security import HTTPBearer, HTTPAuthCredential
   ```

2. **CORS Configuration**: Set specific allowed origins
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       ...
   )
   ```

3. **Rate Limiting**: Add rate limiting
   ```bash
   pip install slowapi
   ```

4. **HTTPS**: Use reverse proxy (nginx) with SSL certificates

## 📞 Support

For issues or questions:
1. Check API docs at `/docs`
2. Review logs in `logs/` directory
3. Test endpoints with curl/Postman
4. Check main project integration in `app/services/`

---

**Dashboard Backend v1.0.0** | Ready for Production
