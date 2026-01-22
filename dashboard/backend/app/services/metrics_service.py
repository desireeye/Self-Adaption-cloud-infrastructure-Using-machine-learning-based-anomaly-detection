"""
Real-time metrics collection service
Collects CPU, Memory, Disk, Network metrics using psutil
"""
import psutil
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and manages real-time system metrics"""
    
    def __init__(self, max_history: int = 3600):
        """
        Initialize metrics collector
        
        Args:
            max_history: Maximum number of metrics to store (default: 3600 = 1 hour at 1Hz)
        """
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()
        
    def collect_metrics(self) -> Dict:
        """
        Collect current system metrics
        
        Returns:
            Dictionary with current metrics and timestamp
        """
        try:
            current_time = time.time()
            time_delta = current_time - self.last_time
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_per_core = psutil.cpu_percent(interval=0, percpu=True)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)
            
            # Network metrics
            net_io = psutil.net_io_counters()
            bytes_sent_delta = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_delta if time_delta > 0 else 0
            bytes_recv_delta = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_delta if time_delta > 0 else 0
            
            self.last_net_io = net_io
            self.last_time = current_time
            
            # Temperature (if available)
            temperature = None
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Get first available temperature sensor
                        first_sensor = list(temps.values())[0]
                        if first_sensor:
                            temperature = first_sensor[0].current
            except Exception as e:
                logger.debug(f"Could not read temperature: {e}")
            
            metric_point = {
                'timestamp': datetime.utcnow(),
                'cpu_percent': cpu_percent,
                'cpu_per_core': cpu_per_core,
                'memory_percent': memory_percent,
                'memory_used_mb': memory_used_mb,
                'memory_available_mb': memory_available_mb,
                'disk_percent': disk_percent,
                'disk_used_gb': disk_used_gb,
                'disk_total_gb': disk_total_gb,
                'network_bytes_sent_per_sec': bytes_sent_delta,
                'network_bytes_recv_per_sec': bytes_recv_delta,
                'temperature': temperature
            }
            
            self.metrics_history.append(metric_point)
            return metric_point
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            raise
    
    def get_latest_metrics(self) -> Dict:
        """Get the most recent metrics point"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return self.collect_metrics()
    
    def get_metrics_range(self, seconds: int = 300) -> List[Dict]:
        """
        Get metrics from the last N seconds
        
        Args:
            seconds: Number of seconds of history to retrieve
            
        Returns:
            List of metric points from the specified time range
        """
        if not self.metrics_history:
            return []
        
        cutoff_time = datetime.utcnow().timestamp() - seconds
        result = []
        
        for metric in self.metrics_history:
            if metric['timestamp'].timestamp() >= cutoff_time:
                result.append(metric)
        
        return result
    
    def get_history(self) -> List[Dict]:
        """Get all stored metrics history"""
        return list(self.metrics_history)
    
    def calculate_statistics(self, seconds: int = 300) -> Dict:
        """
        Calculate statistics for metrics in time range
        
        Args:
            seconds: Time window for statistics
            
        Returns:
            Dictionary with min, max, avg, std values
        """
        metrics_range = self.get_metrics_range(seconds)
        
        if not metrics_range:
            return {}
        
        stats = {
            'cpu': {
                'min': min(m['cpu_percent'] for m in metrics_range),
                'max': max(m['cpu_percent'] for m in metrics_range),
                'avg': sum(m['cpu_percent'] for m in metrics_range) / len(metrics_range)
            },
            'memory': {
                'min': min(m['memory_percent'] for m in metrics_range),
                'max': max(m['memory_percent'] for m in metrics_range),
                'avg': sum(m['memory_percent'] for m in metrics_range) / len(metrics_range)
            },
            'disk': {
                'min': min(m['disk_percent'] for m in metrics_range),
                'max': max(m['disk_percent'] for m in metrics_range),
                'avg': sum(m['disk_percent'] for m in metrics_range) / len(metrics_range)
            }
        }
        
        return stats


# Global instance
_collector = None


def get_collector() -> MetricsCollector:
    """Get or create global metrics collector instance"""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector
