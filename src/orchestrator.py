"""
Main Orchestrator
Coordinates all components: monitoring, preprocessing, detection, decision, recovery
"""

import logging
import time
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

from src.monitoring.resource_monitor import ResourceMonitor
from src.preprocessing.data_preprocessor import DataPreprocessor
from src.anomaly_detection.anomaly_detector import AnomalyDetector, AnomalyAnalyzer
from src.adaptive_engine.decision_engine import AdaptiveDecisionEngine
from src.recovery_actions.recovery_executor import (
    LocalRecoveryExecutor, ActionOrchestrator, RecoveryAction
)

logger = logging.getLogger(__name__)


class SelfAdaptiveOrchestrator:
    """
    Main orchestrator coordinating all self-adaptive system components
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the orchestrator
        
        Args:
            config: Configuration dictionary with component settings
        """
        self.config = config or self._get_default_config()
        
        # Initialize components
        self.monitor = ResourceMonitor(
            max_samples=self.config['monitoring']['max_samples'],
            sampling_interval=self.config['monitoring']['sampling_interval']
        )
        
        self.preprocessor = DataPreprocessor(
            scaler_type=self.config['preprocessing']['scaler_type']
        )
        
        self.detector = AnomalyDetector(
            contamination=self.config['anomaly_detection']['contamination']
        )
        
        self.analyzer = None  # Initialized after detector training
        
        self.decision_engine = AdaptiveDecisionEngine(
            learning_rate=self.config['decision_engine']['learning_rate']
        )
        
        self.executor = LocalRecoveryExecutor()
        self.orchestrator = ActionOrchestrator(self.executor)
        
        # State
        self.is_running = False
        self.system_state = {
            'current_instances': 1,
            'load_average': 0.0,
            'response_time_ms': 0.0,
            'error_rate': 0.0
        }
        
        self.run_statistics = {
            'total_anomalies_detected': 0,
            'total_recoveries_executed': 0,
            'uptime_seconds': 0
        }
    
    @staticmethod
    def _get_default_config() -> Dict:
        """Get default configuration"""
        return {
            'monitoring': {
                'max_samples': 1000,
                'sampling_interval': 1.0
            },
            'preprocessing': {
                'scaler_type': 'standard'
            },
            'anomaly_detection': {
                'contamination': 0.05
            },
            'decision_engine': {
                'learning_rate': 0.1
            },
            'recovery': {
                'executor_type': 'local'
            }
        }
    
    def initialize(self) -> None:
        """Initialize and train the system"""
        logger.info("Initializing Self-Adaptive System...")
        
        # Start monitoring
        self.monitor.start()
        logger.info("Resource monitoring started")
        
        # Collect initial data for training
        logger.info("Collecting training data (30 seconds)...")
        time.sleep(30)
        
        # Get collected metrics
        metrics_list = self.monitor.get_all_metrics()
        
        if len(metrics_list) < 10:
            logger.warning("Insufficient training data collected")
            return
        
        # Preprocess data
        logger.info(f"Preprocessing {len(metrics_list)} metrics...")
        X, df = self.preprocessor.prepare_for_training(metrics_list)
        
        # Train anomaly detector
        logger.info("Training anomaly detection model...")
        self.detector.train(X)
        
        # Initialize analyzer
        self.analyzer = AnomalyAnalyzer(self.detector, self.preprocessor.feature_names)
        
        logger.info("System initialization complete!")
    
    def run(self, duration_seconds: Optional[int] = None) -> None:
        """
        Run the self-adaptive system
        
        Args:
            duration_seconds: How long to run (None = indefinite)
        """
        self.is_running = True
        start_time = time.time()
        
        logger.info(f"Starting self-adaptive monitoring (duration: {duration_seconds or 'infinite'}s)")
        
        try:
            while self.is_running:
                # Check duration
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    logger.info(f"Reached duration limit: {duration_seconds}s")
                    break
                
                # Get current metrics
                current_metrics = self.monitor.get_latest_metrics()
                
                if not current_metrics:
                    time.sleep(1)
                    continue
                
                # Preprocess single sample
                feature_vector = self.preprocessor.prepare_inference_features(current_metrics)
                
                # Detect anomalies
                if self.analyzer:
                    anomaly_data = self.analyzer.analyze_sample(
                        feature_vector,
                        metadata={'timestamp': current_metrics['timestamp']}
                    )
                    
                    # Make decision
                    decision = self.decision_engine.make_decision(anomaly_data, self.system_state)
                    
                    # Execute recovery if needed
                    if decision['action'] != 'monitor':
                        self._execute_recovery(decision)
                        self.run_statistics['total_anomalies_detected'] += 1
                
                # Update uptime
                self.run_statistics['uptime_seconds'] = int(time.time() - start_time)
                
                time.sleep(self.config['monitoring']['sampling_interval'])
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error during execution: {e}", exc_info=True)
        finally:
            self.stop()
    
    def _execute_recovery(self, decision: Dict) -> None:
        """Execute recovery actions based on decision"""
        logger.info(f"Executing recovery: {decision['action']} (severity: {decision['severity']})")
        
        # Plan recovery actions
        actions = self.orchestrator.plan_recovery(decision)
        
        # Execute recovery plan
        summary = self.orchestrator.execute_recovery_plan(actions)
        
        self.run_statistics['total_recoveries_executed'] += 1
        
        logger.info(f"Recovery complete: {summary['successful']}/{summary['total_actions']} actions successful")
    
    def stop(self) -> None:
        """Stop the system"""
        self.is_running = False
        self.monitor.stop()
        logger.info("Self-adaptive system stopped")
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        stats = {
            'uptime_seconds': self.run_statistics['uptime_seconds'],
            'total_anomalies_detected': self.run_statistics['total_anomalies_detected'],
            'total_recoveries_executed': self.run_statistics['total_recoveries_executed'],
        }
        
        if self.analyzer:
            stats['anomaly_statistics'] = self.analyzer.get_anomaly_statistics()
        
        stats['decision_statistics'] = self.decision_engine.get_decision_statistics()
        stats['recovery_statistics'] = self.executor.get_action_statistics()
        
        return stats
    
    def export_results(self, output_dir: str = 'data') -> None:
        """Export all system results and logs"""
        Path(output_dir).mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export metrics
        metrics_file = f"{output_dir}/metrics_{timestamp}.json"
        self.monitor.export_metrics_to_file(metrics_file)
        
        # Export anomaly log
        if self.analyzer:
            anomaly_file = f"{output_dir}/anomalies_{timestamp}.json"
            self.analyzer.export_anomaly_log(anomaly_file)
        
        # Export decision log
        decision_file = f"{output_dir}/decisions_{timestamp}.json"
        self.decision_engine.export_decision_log(decision_file)
        
        # Export action log
        action_file = f"{output_dir}/actions_{timestamp}.json"
        self.executor.export_action_log(action_file)
        
        # Export summary statistics
        summary_file = f"{output_dir}/summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(self.get_statistics(), f, indent=2)
        
        logger.info(f"Results exported to {output_dir}")
    
    def print_status(self) -> None:
        """Print current system status"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("SELF-ADAPTIVE SYSTEM STATUS")
        print("="*60)
        print(f"Uptime: {stats['uptime_seconds']}s")
        print(f"Anomalies Detected: {stats['total_anomalies_detected']}")
        print(f"Recoveries Executed: {stats['total_recoveries_executed']}")
        
        if 'anomaly_statistics' in stats:
            print(f"\nAnomaly Statistics:")
            print(f"  Total Samples: {stats['anomaly_statistics']['total_samples']}")
            print(f"  Anomalies: {stats['anomaly_statistics']['anomalies_detected']}")
            print(f"  Anomaly Rate: {stats['anomaly_statistics']['anomaly_rate']:.2%}")
        
        if 'recovery_statistics' in stats:
            print(f"\nRecovery Statistics:")
            print(f"  Actions Executed: {stats['recovery_statistics']['total_actions']}")
            print(f"  Success Rate: {stats['recovery_statistics']['success_rate']:.2%}")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run orchestrator
    orchestrator = SelfAdaptiveOrchestrator()
    orchestrator.initialize()
    
    # Run for 2 minutes
    try:
        orchestrator.run(duration_seconds=120)
    finally:
        orchestrator.print_status()
        orchestrator.export_results()
