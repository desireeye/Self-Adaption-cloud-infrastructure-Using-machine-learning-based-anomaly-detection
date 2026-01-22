"""
Main FastAPI application setup
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers
from app.api import metrics, anomalies, health

# Create FastAPI app
app = FastAPI(
    title="Self-Adaptive Dashboard API",
    description="Real-time metrics, anomaly detection, and adaptive actions API",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics.router)
app.include_router(anomalies.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Self-Adaptive Cloud Infrastructure Dashboard",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "openapi_schema": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dashboard-api"
    }


@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "name": "Self-Adaptive Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "metrics": {
                "/api/metrics/current": "Get current system metrics",
                "/api/metrics/history": "Get metrics history (configurable time window)",
                "/api/metrics/statistics": "Get metrics statistics (min/max/avg)",
                "/api/metrics/full-history": "Get all stored metrics"
            },
            "anomalies": {
                "/api/anomalies/detect": "Detect anomalies in current metrics",
                "/api/anomalies/model-stats": "Get ML model statistics",
                "/api/anomalies/retrain": "Manually trigger model retraining",
                "/api/anomalies/summary": "Get anomaly summary for time period"
            },
            "health": {
                "/api/health/status": "Get overall system health status",
                "/api/health/trigger-action": "Manually trigger adaptive action",
                "/api/health/actions/history": "Get action execution history",
                "/api/health/actions/active": "Get currently executing actions",
                "/api/health/actions/statistics": "Get action execution statistics"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
