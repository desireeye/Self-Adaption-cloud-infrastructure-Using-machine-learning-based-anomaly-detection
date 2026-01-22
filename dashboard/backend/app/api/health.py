"""
FastAPI routes for health and adaptive actions endpoints
Integrated with main Self-Adaptive System
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
from app.models.metrics import SystemHealth, AdaptiveAction
from app.services.metrics_service import get_collector
from app.services.anomaly_service import get_anomaly_service
from app.services.action_service import get_action_service
from app.services.system_integration import get_system_integration

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/status")
async def get_system_health():
    """
    Get comprehensive system health status
    
    Returns:
        Overall health score, status, recent anomalies, active adaptations
    """
    try:
        collector = get_collector()
        anomaly_service = get_anomaly_service()
        action_service = get_action_service()
        
        # Get current metrics
        metrics = collector.get_latest_metrics()
        
        # Detect current anomaly
        anomaly_result = anomaly_service.detect_anomaly(metrics)
        
        # Calculate health score (0-100)
        # Lower metrics usage = higher health
        cpu_score = max(0, 100 - metrics['cpu_percent'])
        memory_score = max(0, 100 - metrics['memory_percent'])
        disk_score = max(0, 100 - metrics['disk_percent'])
        anomaly_score = (1.0 - anomaly_result['anomaly_score']) * 100
        
        health_score = (cpu_score + memory_score + disk_score + anomaly_score) / 4
        
        # Determine status
        if anomaly_result['anomaly_level'] == 'emergency':
            status = 'critical'
        elif anomaly_result['anomaly_level'] == 'critical':
            status = 'recovering'
        elif anomaly_result['is_anomaly']:
            status = 'adapting'
        else:
            status = 'stable'
        
        # Get recent actions
        recent_actions = action_service.get_action_history(limit=5)
        
        # Count anomalies in last hour
        metrics_hour = collector.get_metrics_range(3600)
        anomalies_count = 0
        last_anomaly_time = None
        for m in metrics_hour:
            result = anomaly_service.detect_anomaly(m)
            if result['is_anomaly']:
                anomalies_count += 1
                if last_anomaly_time is None:
                    last_anomaly_time = result['timestamp']
        
        return SystemHealth(
            timestamp=datetime.utcnow(),
            status=status,
            health_score=health_score,
            metrics={
                'timestamp': metrics['timestamp'],
                'cpu_percent': metrics['cpu_percent'],
                'memory_percent': metrics['memory_percent'],
                'disk_percent': metrics['disk_percent'],
                'network_bytes_sent': metrics['network_bytes_sent_per_sec'],
                'network_bytes_recv': metrics['network_bytes_recv_per_sec'],
                'temperature': metrics.get('temperature')
            },
            last_anomaly_detected=last_anomaly_time,
            anomalies_in_last_hour=anomalies_count,
            active_adaptations=len(action_service.get_active_actions()),
            recent_actions=[
                AdaptiveAction(
                    timestamp=a['timestamp'],
                    action_type=a['action_type'],
                    target=a['target'],
                    status=a['status'],
                    impact_estimate=a['impact_estimate'],
                    reason=a['reason']
                )
                for a in recent_actions
            ]
        )
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-action")
async def trigger_action(action_type: str, target: str, reason: str = "Manual trigger", 
                         impact_estimate: float = 0.0):
    """
    Manually trigger a self-adaptive action
    
    Args:
        action_type: Type of action (scale_up, scale_down, restart_service, etc)
        target: Target resource or service
        reason: Reason for action
        impact_estimate: Estimated impact percentage
    
    Returns:
        Action execution result
    """
    try:
        action_service = get_action_service()
        result = action_service.execute_action(action_type, target, reason, impact_estimate)
        return result
    except Exception as e:
        logger.error(f"Error triggering action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions/history")
async def get_action_history(limit: int = 100):
    """
    Get action execution history
    
    Args:
        limit: Maximum number of actions to return
    
    Returns:
        List of executed actions
    """
    try:
        action_service = get_action_service()
        history = action_service.get_action_history(limit)
        return {'count': len(history), 'actions': history}
    except Exception as e:
        logger.error(f"Error getting action history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions/active")
async def get_active_actions():
    """
    Get currently executing actions
    
    Returns:
        List of active actions
    """
    try:
        action_service = get_action_service()
        active = action_service.get_active_actions()
        return {'count': len(active), 'actions': active}
    except Exception as e:
        logger.error(f"Error getting active actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions/statistics")
async def get_action_statistics():
    """
    Get action execution statistics
    
    Returns:
        Success rate, breakdown by type, average impact
    """
    try:
        action_service = get_action_service()
        stats = action_service.get_action_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting action statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-summary")
async def get_system_summary():
    """
    Get comprehensive system summary from main Self-Adaptive System
    
    Returns:
        Complete system status including metrics, anomalies, decisions
    """
    try:
        system_integration = get_system_integration()
        summary = system_integration.get_system_summary()
        return summary
    except Exception as e:
        logger.error("Error getting system summary: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/integrated-status")
async def get_integrated_status():
    """
    Get integrated health status combining real-time and historical data
    
    Returns:
        Combined health score from both services
    """
    try:
        system_integration = get_system_integration()
        health = system_integration.get_health_status()
        return health
    except Exception as e:
        logger.error("Error getting integrated status: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-availability")
async def get_data_availability():
    """
    Check data availability from main system
    
    Returns:
        Information about available data files and their locations
    """
    try:
        system_integration = get_system_integration()
        
        metrics_file = system_integration.get_latest_metrics_file()
        anomalies_file = system_integration.get_latest_anomalies_file()
        decisions_file = system_integration.get_latest_decisions_file()
        
        metrics = system_integration.load_metrics_history(limit=1)
        anomalies = system_integration.load_anomalies_history(limit=1)
        decisions = system_integration.load_decisions_history(limit=1)
        
        return {
            'status': 'connected' if metrics_file else 'no_data',
            'data_available': {
                'metrics': metrics_file is not None,
                'anomalies': anomalies_file is not None,
                'decisions': decisions_file is not None
            },
            'file_paths': {
                'metrics': metrics_file,
                'anomalies': anomalies_file,
                'decisions': decisions_file
            },
            'last_data': {
                'metrics': metrics[0] if metrics else None,
                'anomalies': anomalies[0] if anomalies else None,
                'decisions': decisions[0] if decisions else None
            },
            'integration_status': 'READY - Connected to main Self-Adaptive System'
        }
    except Exception as e:
        logger.error("Error getting data availability: %s", e)
        return {
            'status': 'error',
            'error': str(e),
            'integration_status': 'ERROR - Unable to connect to main system'
        }
