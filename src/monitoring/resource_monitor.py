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
        self.max_samples = max_samples
        self.sampling_interval = sampling_interval
        self.is_monitoring = False
        self.monitor_thread = None

        # Data buffers
        self.metrics = deque(maxlen=max_samples)
        self.lock = threading.Lock()

        # Previous network stats
        self.prev_net_io = None

    def start(self) -> None:
        """Start continuous monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True
        )
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
                logger.error("Error collecting metrics: %s", e)

            time.sleep(self.sampling_interval)

    def collect_metrics(self) -> Dict:
        """Collect current system metrics"""
        timestamp = datetime.now().isoformat()

        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net_io = psutil.net_io_counters()

        return {
            "timestamp": timestamp,
            "cpu": {
                "percent": cpu_percent,
                "cores": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None,
            },
            "memory": {
                "total_mb": memory.total / (1024 ** 2),
                "used_mb": memory.used / (1024 ** 2),
                "available_mb": memory.available / (1024 ** 2),
                "percent": memory.percent,
            },
            "disk": {
                "total_gb": disk.total / (1024 ** 3),
                "used_gb": disk.used / (1024 ** 3),
                "free_gb": disk.free / (1024 ** 3),
                "percent": disk.percent,
            },
            "network": self._calculate_network_metrics(net_io),
            "top_processes": self._get_top_processes(),
        }

    def _calculate_network_metrics(self, net_io) -> Dict:
        """Calculate network throughput metrics"""
        metrics = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "bytes_sent_per_sec": 0.0,
            "bytes_recv_per_sec": 0.0,
        }

        if self.prev_net_io:
            delta = self.sampling_interval
            metrics["bytes_sent_per_sec"] = (
                net_io.bytes_sent - self.prev_net_io.bytes_sent
            ) / delta
            metrics["bytes_recv_per_sec"] = (
                net_io.bytes_recv - self.prev_net_io.bytes_recv
            ) / delta

        self.prev_net_io = net_io
        return metrics

    def _get_top_processes(self, limit: int = 5) -> List[Dict]:
        """Get top processes by CPU usage"""
        processes: List[Dict] = []
        try:
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent"]
            ):
                processes.append(proc.info)

            processes.sort(
                key=lambda x: x.get("cpu_percent", 0.0), reverse=True
            )
            return processes[:limit]

        except Exception as e:
            logger.warning("Error getting process info: %s", e)
            return []

    def get_latest_metrics(self) -> Optional[Dict]:
        """Get the most recent metrics"""
        with self.lock:
            return self.metrics[-1] if self.metrics else None

    def get_all_metrics(self) -> List[Dict]:
        """Get all collected metrics"""
        with self.lock:
            return list(self.metrics)

    def export_metrics_to_file(self, filepath: str) -> None:
        """Export all metrics to a JSON file"""
        with self.lock:
            with open(filepath, "w") as f:
                json.dump(list(self.metrics), f, indent=2)
        logger.info("Metrics exported to %s", filepath)


class ResourceThresholds:
    """Define resource thresholds for anomaly detection"""

    def __init__(self):
        self.cpu_high = 80.0
        self.memory_high = 85.0
        self.disk_high = 90.0
        self.network_burst = 1e9  # bytes/sec

    def check_thresholds(self, metrics: Dict) -> Dict[str, bool]:
        return {
            "cpu_exceeded": metrics["cpu"]["percent"] > self.cpu_high,
            "memory_exceeded": metrics["memory"]["percent"] > self.memory_high,
            "disk_exceeded": metrics["disk"]["percent"] > self.disk_high,
            "network_burst": (
                metrics["network"]["bytes_sent_per_sec"] > self.network_burst
                or metrics["network"]["bytes_recv_per_sec"] > self.network_burst
            ),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    monitor = ResourceMonitor(sampling_interval=0.5)
    monitor.start()

    try:
        for i in range(5):
            time.sleep(1)
            latest = monitor.get_latest_metrics()
            if latest:
                print(f"\nSnapshot {i + 1}")
                print(f"CPU: {latest['cpu']['percent']:.1f}%")
                print(f"Memory: {latest['memory']['percent']:.1f}%")
                print(f"Disk: {latest['disk']['percent']:.1f}%")
    finally:
        monitor.stop()
