"""
Resource Monitoring Module
Monitors system resources: CPU, RAM, Disk, Network
Real-time collection with thread-based continuous monitoring
"""

import psutil
import time
import threading
import json
from datetime import datetime
from collections import deque
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ResourceMonitor:
    """
    Monitors system resources in real-time.
    Collects CPU, Memory, Disk, and Network metrics.
    """

    def __init__(self, max_samples: int = 1000, sampling_interval: float = 1.0):
        """
        Initialize ResourceMonitor
        
        Args:
            max_samples: Maximum samples to keep in memory
            sampling_interval: Time between samples in seconds
        """
        self.max_samples = max_samples
        self.sampling_interval = sampling_interval
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Data buffers (using deque for fixed-size FIFO)
        self.metrics = deque(maxlen=max_samples)
        self.lock = threading.Lock()
        
        # Store previous network stats for delta calculation
        self.prev_net_io = None
        
    def start(self) -> None:
        """Start continuous monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Resource monitoring started")
    
    def stop(self) -> None:
        """Stop monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metric = self.collect_metrics()
                with self.lock:
                    self.metrics.append(metric)
        except (OSError, AttributeError) as e:
            logger.error("Error collecting metrics: %s", e)            time.sleep(self.sampling_interval)
    
    def collect_metrics(self) -> Dict:
        """
        Collect current system metrics
        
        Returns:
            Dictionary with all metrics
        """
        timestamp = datetime.now().isoformat()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        net_io = psutil.net_io_counters()
        net_metrics = self._calculate_network_metrics(net_io)
        
        # Process metrics (top processes by CPU and memory)
        top_processes = self._get_top_processes()
        
        metric = {
            'timestamp': timestamp,
            'cpu': {
                'percent': cpu_percent,
                'cores': cpu_count,
                'frequency_mhz': cpu_freq.current if cpu_freq else None
            },
            'memory': {
                'total_mb': memory.total / (1024 ** 2),
                'used_mb': memory.used / (1024 ** 2),
                'available_mb': memory.available / (1024 ** 2),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': disk.total / (1024 ** 3),
                'used_gb': disk.used / (1024 ** 3),
                'free_gb': disk.free / (1024 ** 3),
                'percent': disk.percent
            },
            'network': net_metrics,
            'top_processes': top_processes
        }
        
        return metric
    
    def _calculate_network_metrics(self, net_io) -> Dict:
        """Calculate network throughput metrics"""
        metrics = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'bytes_sent_per_sec': 0,
            'bytes_recv_per_sec': 0
        }
        
        if self.prev_net_io:
            time_delta = self.sampling_interval
            metrics['bytes_sent_per_sec'] = (net_io.bytes_sent - self.prev_net_io.bytes_sent) / time_delta
            metrics['bytes_recv_per_sec'] = (net_io.bytes_recv - self.prev_net_io.bytes_recv) / time_delta
        
        self.prev_net_io = net_io
        return metrics
    
    def _get_top_processes(self, limit: int = 5) -> List[Dict]:
        """Get top processes by CPU usage"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                processes.append(proc.info)
            
            # Sort by CPU and return top
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:limit]
        except Exception as e:
            logger.warning(f"Error getting process info: {e}")
            return []
    
    def get_latest_metrics(self) -> Optional[Dict]:
        """Get the most recent metrics"""
        with self.lock:
            return self.metrics[-1] if self.metrics else None
    
    def get_all_metrics(self) -> List[Dict]:
        """Get all collected metrics"""
        with self.lock:
            return list(self.metrics)
    
    def get_metrics_window(self, duration_seconds: int) -> List[Dict]:
        """
        Get metrics from the last N seconds
        
        Args:
            duration_seconds: Time window in seconds
            
        Returns:
            List of metrics within the time window
        """
        with self.lock:
            if not self.metrics:
                return []
            
            cutoff_time = datetime.fromisoformat(self.metrics[-1]['timestamp'])
            cutoff_time = cutoff_time.replace(
                microsecond=int((cutoff_time.microsecond - duration_seconds * 1e6) % 1e6)
            )
            
            result = []
            for metric in reversed(self.metrics):
                metric_time = datetime.fromisoformat(metric['timestamp'])
                if (cutoff_time - metric_time).total_seconds() <= duration_seconds:
                    result.append(metric)
                else:
                    break
            
            return list(reversed(result))
    
    def get_average_metrics(self, duration_seconds: int = 60) -> Optional[Dict]:
        """
        Calculate average metrics over a time window
        
        Args:
            duration_seconds: Time window in seconds
            
        Returns:
            Dictionary with averaged metrics
        """
        window_metrics = self.get_metrics_window(duration_seconds)
        
        if not window_metrics:
            return None
        
        avg = {
            'cpu_percent': sum(m['cpu']['percent'] for m in window_metrics) / len(window_metrics),
            'memory_percent': sum(m['memory']['percent'] for m in window_metrics) / len(window_metrics),
            'disk_percent': sum(m['disk']['percent'] for m in window_metrics) / len(window_metrics),
            'sample_count': len(window_metrics)
        }
        
        return avg
    
    def export_metrics_to_file(self, filepath: str) -> None:
        """Export all metrics to JSON file"""
        with self.lock:
            with open(filepath, 'w') as f:
                json.dump(list(self.metrics), f, indent=2)
        logger.info(f"Metrics exported to {filepath}")


class ResourceThresholds:
    """Define resource thresholds for anomaly detection"""
    
    def __init__(self):
        self.cpu_high = 80.0  # CPU > 80%
        self.memory_high = 85.0  # Memory > 85%
        self.disk_high = 90.0  # Disk > 90%
        self.network_burst = 1e9  # Network > 1GB/sec
    
    def check_thresholds(self, metrics: Dict) -> Dict[str, bool]:
        """
        Check if metrics exceed thresholds
        
        Returns:
            Dictionary indicating which metrics are anomalous
        """
        return {
            'cpu_exceeded': metrics['cpu']['percent'] > self.cpu_high,
            'memory_exceeded': metrics['memory']['percent'] > self.memory_high,
            'disk_exceeded': metrics['disk']['percent'] > self.disk_high,
            'network_burst': metrics['network']['bytes_sent_per_sec'] > self.network_burst or
                           metrics['network']['bytes_recv_per_sec'] > self.network_burst
        }


if __name__ == "__main__":
    # Test monitoring
    logging.basicConfig(level=logging.INFO)
    
    monitor = ResourceMonitor(sampling_interval=0.5)
    monitor.start()
    
    try:
        for i in range(10):
            time.sleep(1)
            latest = monitor.get_latest_metrics()
            if latest:
                print(f"\nMetrics snapshot {i+1}:")
                print(f"  CPU: {latest['cpu']['percent']:.1f}%")
                print(f"  Memory: {latest['memory']['percent']:.1f}%")
                print(f"  Disk: {latest['disk']['percent']:.1f}%")
    finally:
        monitor.stop()
