"""
Self-Adaptive Decision Engine
Makes intelligent decisions based on anomaly detection and system state
Implements dynamic thresholds and learning policies
"""

import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import json
import numpy as np

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Anomaly severity levels"""
    NORMAL = 0
    WARNING = 1
    CRITICAL = 2
    EMERGENCY = 3


class AdaptiveDecisionEngine:
    """
    Intelligent decision engine that adapts to system behavior
    Makes decisions about scaling, recovery, and resource allocation
    """
    
    def __init__(self, learning_rate: float = 0.1, history_window: int = 100):
        """
        Initialize AdaptiveDecisionEngine
        
        Args:
            learning_rate: Rate of threshold adaptation (0 to 1)
            history_window: Number of decisions to keep in history
        """
        self.learning_rate = learning_rate
        self.history_window = history_window
        
        # Dynamic thresholds
        self.thresholds = {
            'cpu_warning': 60.0,
            'cpu_critical': 80.0,
            'memory_warning': 65.0,
            'memory_critical': 85.0,
            'disk_warning': 75.0,
            'disk_critical': 90.0,
            'anomaly_probability_threshold': 0.7
        }
        
        # Decision history for learning
        self.decision_history = []
        self.outcome_history = []
        
        # Current state
        self.last_decision = None
        self.decision_timestamp = None
        self.consecutive_anomalies = 0
        self.anomaly_cooldown = timedelta(seconds=30)
        self.last_anomaly_time = None
        
        # Metrics for adaptation
        self.false_positive_rate = 0.0
        self.true_positive_rate = 0.95
        self.decision_effectiveness = {}
    
    def assess_anomaly_severity(self, anomaly_data: Dict) -> SeverityLevel:
        """
        Assess the severity of an anomaly
        
        Args:
            anomaly_data: Dictionary with anomaly information
                - is_anomaly: bool
                - anomaly_probability: float
                - feature_values: dict with metric values
                - contributing_features: list of anomalous features
                
        Returns:
            SeverityLevel enum
        """
        if not anomaly_data.get('is_anomaly', False):
            return SeverityLevel.NORMAL
        
        probability = anomaly_data.get('anomaly_probability', 0)
        features = anomaly_data.get('feature_values', {})
        
        # Check resource utilization
        cpu = features.get('cpu_percent', 0)
        memory = features.get('memory_percent', 0)
        disk = features.get('disk_percent', 0)
        
        # Determine severity
        if probability > 0.9 and (cpu > 85 or memory > 85 or disk > 90):
            return SeverityLevel.EMERGENCY
        elif probability > 0.8 and (cpu > 80 or memory > 80 or disk > 85):
            return SeverityLevel.CRITICAL
        elif probability > 0.7:
            return SeverityLevel.WARNING
        else:
            return SeverityLevel.NORMAL
    
    def make_decision(self, anomaly_data: Dict, system_state: Dict) -> Dict:
        """
        Make a decision about system actions
        
        Args:
            anomaly_data: Anomaly detection results
            system_state: Current system state
                - current_instances: int
                - load_average: float
                - response_time_ms: float
                - error_rate: float
                
        Returns:
            Decision dictionary with recommended actions
        """
        severity = self.assess_anomaly_severity(anomaly_data)
        
        # Check cooldown period
        if self.last_anomaly_time:
            if datetime.now() - self.last_anomaly_time < self.anomaly_cooldown:
                logger.debug("In anomaly cooldown period, reducing decision frequency")
                return {
                    'action': 'none',
                    'severity': severity.name,
                    'reason': 'cooldown_period',
                    'confidence': 0.0
                }
        
        # Update consecutive anomaly counter
        if severity != SeverityLevel.NORMAL:
            self.consecutive_anomalies += 1
            self.last_anomaly_time = datetime.now()
        else:
            self.consecutive_anomalies = 0
        
        # Generate decision based on severity
        decision = self._generate_decision(severity, anomaly_data, system_state)
        
        # Store in history
        self._record_decision(decision, anomaly_data)
        
        return decision
    
    def _generate_decision(self, severity: SeverityLevel, 
                          anomaly_data: Dict, system_state: Dict) -> Dict:
        """Generate appropriate decision based on severity"""
        
        features = anomaly_data.get('feature_values', {})
        cpu = features.get('cpu_percent', 0)
        memory = features.get('memory_percent', 0)
        disk = features.get('disk_percent', 0)
        
        if severity == SeverityLevel.NORMAL:
            return {
                'action': 'monitor',
                'severity': severity.name,
                'reason': 'normal_operation',
                'scale_factor': 1.0,
                'confidence': 1.0,
                'details': {}
            }
        
        elif severity == SeverityLevel.WARNING:
            action = self._select_warning_action(cpu, memory, disk)
            return {
                'action': action,
                'severity': severity.name,
                'reason': 'resource_warning',
                'scale_factor': 1.1,
                'confidence': 0.7,
                'details': {
                    'recommended_scaling': 'increase_monitoring_frequency',
                    'estimated_recovery_time': '5-10 minutes'
                }
            }
        
        elif severity == SeverityLevel.CRITICAL:
            return {
                'action': 'scale_up',
                'severity': severity.name,
                'reason': 'resource_critical',
                'scale_factor': 1.5,
                'confidence': 0.85,
                'details': {
                    'add_instances': max(1, self.consecutive_anomalies // 2),
                    'add_memory': '20%',
                    'estimated_recovery_time': '2-5 minutes'
                }
            }
        
        else:  # EMERGENCY
            return {
                'action': 'emergency_scale',
                'severity': severity.name,
                'reason': 'system_emergency',
                'scale_factor': 2.0,
                'confidence': 0.95,
                'details': {
                    'add_instances': max(2, self.consecutive_anomalies),
                    'add_memory': '50%',
                    'enable_auto_recovery': True,
                    'notify_admin': True,
                    'estimated_recovery_time': '1-2 minutes'
                }
            }
    
    def _select_warning_action(self, cpu: float, memory: float, disk: float) -> str:
        """Select specific action for warning severity"""
        if cpu > memory and cpu > disk:
            return 'optimize_cpu'
        elif memory > cpu and memory > disk:
            return 'optimize_memory'
        elif disk > cpu and disk > memory:
            return 'optimize_disk'
        else:
            return 'monitor'
    
    def adapt_thresholds(self, effectiveness: Dict) -> None:
        """
        Adapt thresholds based on decision effectiveness
        
        Args:
            effectiveness: Dictionary with effectiveness metrics
                - true_positives: int
                - false_positives: int
                - false_negatives: int
        """
        tp = effectiveness.get('true_positives', 0)
        fp = effectiveness.get('false_positives', 0)
        fn = effectiveness.get('false_negatives', 0)
        
        total = tp + fp + fn
        if total == 0:
            return
        
        # Calculate rates
        new_tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        new_fpr = fp / (fp + fn) if (fp + fn) > 0 else 0 if fn > 0 else 1
        
        # Adapt if rates have changed significantly
        if abs(new_tpr - self.true_positive_rate) > 0.05:
            self.true_positive_rate += self.learning_rate * (new_tpr - self.true_positive_rate)
            logger.info(f"Adapted TPR to {self.true_positive_rate:.3f}")
        
        if abs(new_fpr - self.false_positive_rate) > 0.05:
            self.false_positive_rate += self.learning_rate * (new_fpr - self.false_positive_rate)
            logger.info(f"Adapted FPR to {self.false_positive_rate:.3f}")
            
            # Adjust anomaly probability threshold
            if self.false_positive_rate > 0.1:
                self.thresholds['anomaly_probability_threshold'] += 0.05
            elif self.false_positive_rate < 0.05:
                self.thresholds['anomaly_probability_threshold'] -= 0.05
    
    def _record_decision(self, decision: Dict, anomaly_data: Dict) -> None:
        """Record decision in history for learning"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'decision': decision['action'],
            'severity': decision['severity'],
            'anomaly_probability': anomaly_data.get('anomaly_probability', 0),
            'confidence': decision['confidence']
        }
        
        self.decision_history.append(record)
        if len(self.decision_history) > self.history_window:
            self.decision_history.pop(0)
        
        self.last_decision = decision
        self.decision_timestamp = datetime.now()
    
    def get_decision_statistics(self) -> Dict:
        """Get statistics about made decisions"""
        if not self.decision_history:
            return {
                'total_decisions': 0,
                'average_confidence': 0.0,
                'action_distribution': {}
            }
        
        actions = [d['decision'] for d in self.decision_history]
        confidences = [d['confidence'] for d in self.decision_history]
        
        from collections import Counter
        action_counts = Counter(actions)
        
        return {
            'total_decisions': len(self.decision_history),
            'average_confidence': float(np.mean(confidences)),
            'max_confidence': float(np.max(confidences)),
            'min_confidence': float(np.min(confidences)),
            'action_distribution': dict(action_counts),
            'most_common_action': max(action_counts, key=action_counts.get)
        }
    
    def export_decision_log(self, filepath: str) -> None:
        """Export decision history to file"""
        with open(filepath, 'w') as f:
            json.dump(self.decision_history, f, indent=2)
        logger.info(f"Decision log exported to {filepath}")
    
    def reset_statistics(self) -> None:
        """Reset all statistics and history"""
        self.decision_history = []
        self.outcome_history = []
        self.consecutive_anomalies = 0
        self.last_anomaly_time = None
        logger.info("Statistics reset")


class PolicyOptimizer:
    """
    Optimizes adaptive policies based on past outcomes
    """
    
    def __init__(self, engine: AdaptiveDecisionEngine):
        """Initialize policy optimizer"""
        self.engine = engine
        self.policy_metrics = {}
    
    def evaluate_policy(self, outcomes: List[Dict]) -> Dict:
        """
        Evaluate how well the current policy is working
        
        Args:
            outcomes: List of decision outcomes
            
        Returns:
            Evaluation metrics
        """
        if not outcomes:
            return {'success_rate': 0.0, 'avg_recovery_time': 0}
        
        successful = sum(1 for o in outcomes if o.get('success', False))
        recovery_times = [o.get('recovery_time', 0) for o in outcomes if 'recovery_time' in o]
        
        return {
            'success_rate': successful / len(outcomes),
            'avg_recovery_time': np.mean(recovery_times) if recovery_times else 0,
            'total_decisions': len(outcomes),
            'decisions_requiring_escalation': sum(1 for o in outcomes if not o.get('success', True))
        }
    
    def recommend_policy_update(self, evaluation: Dict) -> Optional[Dict]:
        """
        Recommend updates to the adaptive policy
        
        Args:
            evaluation: Policy evaluation results
            
        Returns:
            Recommended policy changes or None
        """
        success_rate = evaluation.get('success_rate', 0)
        avg_recovery = evaluation.get('avg_recovery_time', 0)
        
        recommendations = []
        
        if success_rate < 0.8:
            recommendations.append({
                'type': 'increase_thresholds',
                'reason': 'Low success rate indicates over-aggressive scaling',
                'impact': 'Reduce false positives'
            })
        
        if avg_recovery > 300:  # 5 minutes
            recommendations.append({
                'type': 'increase_resource_allocation',
                'reason': 'Recovery taking too long',
                'impact': 'Faster anomaly recovery'
            })
        
        if success_rate > 0.95:
            recommendations.append({
                'type': 'optimize_costs',
                'reason': 'High success rate with good performance',
                'impact': 'Potential cost reduction'
            })
        
        return recommendations if recommendations else None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test decision engine
    engine = AdaptiveDecisionEngine()
    
    # Simulate anomaly
    anomaly_data = {
        'is_anomaly': True,
        'anomaly_probability': 0.85,
        'feature_values': {
            'cpu_percent': 82,
            'memory_percent': 78,
            'disk_percent': 45
        },
        'contributing_features': ['cpu_percent', 'memory_percent']
    }
    
    system_state = {
        'current_instances': 3,
        'load_average': 2.5,
        'response_time_ms': 150,
        'error_rate': 0.02
    }
    
    decision = engine.make_decision(anomaly_data, system_state)
    print(f"Decision: {decision}")
    print(f"Statistics: {engine.get_decision_statistics()}")
