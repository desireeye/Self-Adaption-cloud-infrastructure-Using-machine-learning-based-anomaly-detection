"""
FastAPI routes for metrics endpoints
Real-time system metrics API
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
from app.models.metrics import SystemMetrics, HistoricalData
from app.services.metrics_service import get_collector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/current", response_model=SystemMetrics)
async def get_current_metrics():
    """
    Get current system metrics
    
    Returns:
        Current system metrics (CPU, Memory, Disk, Network)
    """
    try:
        collector = get_collector()
        metrics = collector.collect_metrics()
        
        return SystemMetrics(
            timestamp=metrics['timestamp'],
            cpu_percent=metrics['cpu_percent'],
            memory_percent=metrics['memory_percent'],
            disk_percent=metrics['disk_percent'],
            network_bytes_sent=metrics['network_bytes_sent_per_sec'],
            network_bytes_recv=metrics['network_bytes_recv_per_sec'],
            temperature=metrics.get('temperature')
        )
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_metrics_history(seconds: int = 300):
    """
    Get metrics history for specified time period
    
    Args:
        seconds: Number of seconds of history (default: 300 = 5 minutes)
    
    Returns:
        Historical data with timestamps and metric values
    """
    try:
        collector = get_collector()
        metrics_range = collector.get_metrics_range(seconds)
        
        if not metrics_range:
            return {
                'timestamps': [],
                'cpu_values': [],
                'memory_values': [],
                'disk_values': [],
                'anomaly_flags': [],
                'anomaly_scores': []
            }
        
        return {
            'timestamps': [m['timestamp'].isoformat() for m in metrics_range],
            'cpu_values': [m['cpu_percent'] for m in metrics_range],
            'memory_values': [m['memory_percent'] for m in metrics_range],
            'disk_values': [m['disk_percent'] for m in metrics_range],
            'anomaly_flags': [False] * len(metrics_range),  # Will be set by anomaly detection
            'anomaly_scores': [0.0] * len(metrics_range)
        }
    except Exception as e:
        logger.error(f"Error getting metrics history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_metrics_statistics(seconds: int = 300):
    """
    Get statistics for metrics in time period
    
    Args:
        seconds: Time window for statistics (default: 300)
    
    Returns:
        Min, max, average values for CPU, Memory, Disk
    """
    try:
        collector = get_collector()
        stats = collector.calculate_statistics(seconds)
        return stats
    except Exception as e:
        logger.error(f"Error getting metrics statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/full-history")
async def get_full_history():
    """
    Get all stored metrics history
    
    Returns:
        All metric points currently stored in memory
    """
    try:
        collector = get_collector()
        history = collector.get_history()
        
        return {
            'count': len(history),
            'metrics': [
                {
                    'timestamp': m['timestamp'].isoformat(),
                    'cpu_percent': m['cpu_percent'],
                    'memory_percent': m['memory_percent'],
                    'disk_percent': m['disk_percent'],
                    'network_bytes_sent_per_sec': m['network_bytes_sent_per_sec'],
                    'network_bytes_recv_per_sec': m['network_bytes_recv_per_sec'],
                    'temperature': m.get('temperature')
                }
                for m in history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting full history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
