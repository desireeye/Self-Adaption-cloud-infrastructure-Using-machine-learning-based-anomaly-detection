"""
FastAPI routes for anomaly detection endpoints
Real-time anomaly detection API
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import logging
from typing import Optional
from app.models.metrics import AnomalyDetectionResult
from app.services.anomaly_service import get_anomaly_service
from app.services.metrics_service import get_collector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


@router.get("/detect", response_model=AnomalyDetectionResult)
async def detect_anomaly():
    """
    Detect anomalies in current system metrics
    
    Returns:
        Anomaly detection result with score, level, and affected metrics
    """
    try:
        # Get current metrics
        collector = get_collector()
        metrics = collector.get_latest_metrics()
        
        # Detect anomaly
        anomaly_service = get_anomaly_service()
        result = anomaly_service.detect_anomaly(metrics)
        
        return AnomalyDetectionResult(
            timestamp=result['timestamp'],
            is_anomaly=result['is_anomaly'],
            anomaly_score=result['anomaly_score'],
            anomaly_level=result['anomaly_level'],
            confidence=result['confidence'],
            affected_metrics=result['affected_metrics'],
            feature_importances=result['feature_importances']
        )
    except Exception as e:
        logger.error(f"Error detecting anomaly: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-stats")
async def get_model_statistics():
    """
    Get ML model statistics and performance metrics
    
    Returns:
        Model type, accuracy, precision, recall, training status
    """
    try:
        anomaly_service = get_anomaly_service()
        stats = anomaly_service.get_model_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting model stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retrain")
async def retrain_model():
    """
    Manually trigger model retraining
    
    Returns:
        Retraining result and status
    """
    try:
        anomaly_service = get_anomaly_service()
        success = anomaly_service.retrain_model()
        
        return {
            'success': success,
            'message': 'Model retrained successfully' if success else 'Insufficient training data',
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retraining model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_anomaly_summary(hours: int = Query(1, ge=1, le=24)):
    """
    Get anomaly detection summary for time period
    
    Args:
        hours: Number of hours to summarize (1-24)
    
    Returns:
        Count of anomalies, distribution by level, affected metrics
    """
    try:
        collector = get_collector()
        anomaly_service = get_anomaly_service()
        
        # Get metrics from time period
        seconds = hours * 3600
        metrics_range = collector.get_metrics_range(seconds)
        
        # Detect anomalies for all metrics
        anomalies = []
        for metrics in metrics_range:
            result = anomaly_service.detect_anomaly(metrics)
            if result['is_anomaly']:
                anomalies.append(result)
        
        # Summarize
        by_level = {}
        affected_metrics_set = set()
        
        for anomaly in anomalies:
            level = anomaly['anomaly_level']
            by_level[level] = by_level.get(level, 0) + 1
            affected_metrics_set.update(anomaly['affected_metrics'])
        
        return {
            'time_period_hours': hours,
            'total_anomalies': len(anomalies),
            'anomalies_by_level': by_level,
            'affected_metrics': list(affected_metrics_set),
            'anomaly_rate': len(anomalies) / len(metrics_range) if metrics_range else 0.0
        }
    except Exception as e:
        logger.error(f"Error getting anomaly summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
