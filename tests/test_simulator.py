"""
Testing and Simulation Module
Tests system components and simulates various anomaly scenarios
"""

import logging
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class AnomalySimulator:
    """
    Simulates different types of anomalies for testing
    """
    
    @staticmethod
    def create_normal_metrics(samples: int = 100) -> List[Dict]:
        """Create normal baseline metrics"""
        metrics = []
        timestamp = datetime.now()
        
        for i in range(samples):
            metric = {
                'timestamp': timestamp.isoformat(),
                'cpu': {
                    'percent': np.random.normal(loc=35, scale=10),
                    'cores': 4,
                    'frequency_mhz': 2400
                },
                'memory': {
                    'total_mb': 8192,
                    'used_mb': np.random.normal(loc=3000, scale=500),
                    'available_mb': 4000,
                    'percent': np.random.normal(loc=45, scale=8)
                },
                'disk': {
                    'total_gb': 256,
                    'used_gb': np.random.normal(loc=128, scale=10),
                    'free_gb': 100,
                    'percent': np.random.normal(loc=50, scale=5)
                },
                'network': {
                    'bytes_sent': 1000000 + np.random.randint(-100000, 100000),
                    'bytes_recv': 1000000 + np.random.randint(-100000, 100000),
                    'packets_sent': 1000,
                    'packets_recv': 1000,
                    'bytes_sent_per_sec': np.random.normal(loc=10000, scale=2000),
                    'bytes_recv_per_sec': np.random.normal(loc=10000, scale=2000)
                },
                'top_processes': []
            }
            
            # Ensure values are non-negative
            metric['cpu']['percent'] = max(0, min(100, metric['cpu']['percent']))
            metric['memory']['percent'] = max(0, min(100, metric['memory']['percent']))
            metric['disk']['percent'] = max(0, min(100, metric['disk']['percent']))
            
            metrics.append(metric)
            timestamp = datetime.fromisoformat(timestamp.isoformat())
            # Would increment timestamp in real usage
        
        return metrics
    
    @staticmethod
    def create_cpu_spike_anomaly(baseline_metrics: List[Dict], 
                                 spike_start: int = 50, 
                                 spike_duration: int = 10) -> List[Dict]:
        """Create CPU spike anomaly"""
        metrics = [m.copy() for m in baseline_metrics]
        
        for i in range(spike_start, min(spike_start + spike_duration, len(metrics))):
            metrics[i]['cpu']['percent'] = np.random.normal(loc=85, scale=5)
            metrics[i]['cpu']['percent'] = max(0, min(100, metrics[i]['cpu']['percent']))
        
        return metrics
    
    @staticmethod
    def create_memory_leak_anomaly(baseline_metrics: List[Dict],
                                   leak_start: int = 50) -> List[Dict]:
        """Create memory leak anomaly (gradual increase)"""
        metrics = [m.copy() for m in baseline_metrics]
        
        for i in range(leak_start, len(metrics)):
            memory_increase = (i - leak_start) * 0.5
            metrics[i]['memory']['percent'] = min(95, 45 + memory_increase)
            metrics[i]['memory']['used_mb'] = min(8000, 3000 + memory_increase * 50)
        
        return metrics
    
    @staticmethod
    def create_network_burst_anomaly(baseline_metrics: List[Dict],
                                    burst_start: int = 50,
                                    burst_duration: int = 5) -> List[Dict]:
        """Create network burst anomaly"""
        metrics = [m.copy() for m in baseline_metrics]
        
        for i in range(burst_start, min(burst_start + burst_duration, len(metrics))):
            metrics[i]['network']['bytes_sent_per_sec'] = np.random.normal(loc=5e8, scale=1e8)
            metrics[i]['network']['bytes_recv_per_sec'] = np.random.normal(loc=5e8, scale=1e8)
        
        return metrics
    
    @staticmethod
    def create_disk_full_anomaly(baseline_metrics: List[Dict],
                                 target_utilization: float = 0.95) -> List[Dict]:
        """Create disk filling up anomaly"""
        metrics = [m.copy() for m in baseline_metrics]
        
        for i in range(len(metrics)):
            progress = i / len(metrics)
            metrics[i]['disk']['percent'] = 50 + progress * 45
            metrics[i]['disk']['used_gb'] = 128 + progress * 120
        
        return metrics
    
    @staticmethod
    def create_combined_anomaly(baseline_metrics: List[Dict]) -> List[Dict]:
        """Create combined multiple anomalies"""
        metrics = [m.copy() for m in baseline_metrics]
        
        # CPU spike (first half)
        for i in range(30, 50):
            metrics[i]['cpu']['percent'] = np.random.normal(loc=82, scale=5)
        
        # Memory leak (second half onwards)
        for i in range(50, len(metrics)):
            leak_progress = (i - 50) / (len(metrics) - 50)
            metrics[i]['memory']['percent'] = 45 + leak_progress * 40
        
        # Network burst (middle)
        for i in range(40, 60):
            metrics[i]['network']['bytes_sent_per_sec'] = np.random.normal(loc=5e8, scale=1e8)
        
        return metrics


class SystemTester:
    """
    Tests the system with simulated anomalies
    """
    
    def __init__(self, orchestrator):
        """Initialize tester with orchestrator instance"""
        self.orchestrator = orchestrator
        self.test_results = []
    
    def test_normal_operation(self) -> Dict:
        """Test system with normal metrics"""
        logger.info("Testing normal operation...")
        
        simulator = AnomalySimulator()
        normal_metrics = simulator.create_normal_metrics(samples=100)
        
        # Preprocess and train on normal data
        X, df = self.orchestrator.preprocessor.prepare_for_training(normal_metrics)
        self.orchestrator.detector.train(X)
        self.orchestrator.analyzer = self.orchestrator.analyzer.__class__(
            self.orchestrator.detector,
            self.orchestrator.preprocessor.feature_names
        )
        
        # Test prediction
        anomalies_detected = 0
        for metric in normal_metrics:
            feature_vector = self.orchestrator.preprocessor.prepare_inference_features(metric)
            anomaly_data = self.orchestrator.analyzer.analyze_sample(feature_vector)
            if anomaly_data['is_anomaly']:
                anomalies_detected += 1
        
        result = {
            'test_name': 'Normal Operation',
            'total_samples': len(normal_metrics),
            'anomalies_detected': anomalies_detected,
            'false_positive_rate': anomalies_detected / len(normal_metrics),
            'status': 'PASS' if anomalies_detected / len(normal_metrics) < 0.15 else 'FAIL'
        }
        
        self.test_results.append(result)
        return result
    
    def test_cpu_spike(self) -> Dict:
        """Test detection of CPU spike anomaly"""
        logger.info("Testing CPU spike detection...")
        
        simulator = AnomalySimulator()
        normal_metrics = simulator.create_normal_metrics(samples=50)
        anomaly_metrics = simulator.create_cpu_spike_anomaly(normal_metrics, spike_start=30, spike_duration=10)
        
        # Train on normal data
        X, df = self.orchestrator.preprocessor.prepare_for_training(normal_metrics)
        self.orchestrator.detector.train(X)
        
        # Test anomaly detection
        spike_start = 30
        anomalies_in_spike = 0
        for i, metric in enumerate(anomaly_metrics[spike_start:spike_start+10]):
            feature_vector = self.orchestrator.preprocessor.prepare_inference_features(metric)
            anomaly_data = self.orchestrator.analyzer.analyze_sample(feature_vector)
            if anomaly_data['is_anomaly']:
                anomalies_in_spike += 1
        
        result = {
            'test_name': 'CPU Spike Detection',
            'spike_samples': 10,
            'detected': anomalies_in_spike,
            'detection_rate': anomalies_in_spike / 10,
            'status': 'PASS' if anomalies_in_spike >= 7 else 'FAIL'
        }
        
        self.test_results.append(result)
        return result
    
    def test_memory_leak(self) -> Dict:
        """Test detection of memory leak anomaly"""
        logger.info("Testing memory leak detection...")
        
        simulator = AnomalySimulator()
        normal_metrics = simulator.create_normal_metrics(samples=50)
        anomaly_metrics = simulator.create_memory_leak_anomaly(normal_metrics, leak_start=30)
        
        # Train on normal data
        X, df = self.orchestrator.preprocessor.prepare_for_training(normal_metrics)
        self.orchestrator.detector.train(X)
        
        # Test anomaly detection in leak period
        leak_start = 30
        anomalies_in_leak = 0
        for metric in anomaly_metrics[leak_start:]:
            feature_vector = self.orchestrator.preprocessor.prepare_inference_features(metric)
            anomaly_data = self.orchestrator.analyzer.analyze_sample(feature_vector)
            if anomaly_data['is_anomaly']:
                anomalies_in_leak += 1
        
        result = {
            'test_name': 'Memory Leak Detection',
            'leak_samples': len(anomaly_metrics) - leak_start,
            'detected': anomalies_in_leak,
            'detection_rate': anomalies_in_leak / (len(anomaly_metrics) - leak_start),
            'status': 'PASS' if anomalies_in_leak >= 5 else 'FAIL'
        }
        
        self.test_results.append(result)
        return result
    
    def test_network_burst(self) -> Dict:
        """Test detection of network burst anomaly"""
        logger.info("Testing network burst detection...")
        
        simulator = AnomalySimulator()
        normal_metrics = simulator.create_normal_metrics(samples=50)
        anomaly_metrics = simulator.create_network_burst_anomaly(normal_metrics, burst_start=30, burst_duration=5)
        
        # Train on normal data
        X, df = self.orchestrator.preprocessor.prepare_for_training(normal_metrics)
        self.orchestrator.detector.train(X)
        
        # Test anomaly detection
        burst_start = 30
        anomalies_in_burst = 0
        for metric in anomaly_metrics[burst_start:burst_start+5]:
            feature_vector = self.orchestrator.preprocessor.prepare_inference_features(metric)
            anomaly_data = self.orchestrator.analyzer.analyze_sample(feature_vector)
            if anomaly_data['is_anomaly']:
                anomalies_in_burst += 1
        
        result = {
            'test_name': 'Network Burst Detection',
            'burst_samples': 5,
            'detected': anomalies_in_burst,
            'detection_rate': anomalies_in_burst / 5,
            'status': 'PASS' if anomalies_in_burst >= 3 else 'FAIL'
        }
        
        self.test_results.append(result)
        return result
    
    def run_all_tests(self) -> List[Dict]:
        """Run all tests"""
        logger.info("Starting comprehensive system tests...")
        
        self.test_results = []
        
        # Run tests
        self.test_normal_operation()
        self.test_cpu_spike()
        self.test_memory_leak()
        self.test_network_burst()
        
        # Print results
        print("\n" + "="*70)
        print("SYSTEM TEST RESULTS")
        print("="*70)
        
        passed = 0
        failed = 0
        
        for result in self.test_results:
            status_symbol = "✓" if result['status'] == "PASS" else "✗"
            print(f"\n{status_symbol} {result['test_name']}")
            
            for key, value in result.items():
                if key not in ['test_name', 'status']:
                    if isinstance(value, float):
                        print(f"  {key}: {value:.2%}" if 0 <= value <= 1 else f"  {key}: {value:.4f}")
                    else:
                        print(f"  {key}: {value}")
            
            if result['status'] == 'PASS':
                passed += 1
            else:
                failed += 1
        
        print("\n" + "="*70)
        print(f"SUMMARY: {passed} passed, {failed} failed")
        print("="*70 + "\n")
        
        return self.test_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create sample metrics
    simulator = AnomalySimulator()
    
    print("Creating test scenarios...")
    normal = simulator.create_normal_metrics(100)
    print(f"Normal metrics: {len(normal)} samples")
    
    cpu_spike = simulator.create_cpu_spike_anomaly(normal)
    print(f"CPU spike anomaly created")
    
    memory_leak = simulator.create_memory_leak_anomaly(normal)
    print(f"Memory leak anomaly created")
    
    combined = simulator.create_combined_anomaly(normal)
    print(f"Combined anomalies created")
