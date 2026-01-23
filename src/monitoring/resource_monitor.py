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

        # Data buffers (fixed-size FIFO)
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
        disk = psutil.disk_usage("/")

        # Network metrics
        net_io = psutil.net_io_counters()
        net_metrics = self._calculate_network_metrics(net_io)

        # Process metrics
        top_processes = self._get_top_processes()

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
            "network": net_metrics,
            "top_processes": top_processes,
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

    def _get_top_processes(self, limit: int = 5) ->_
