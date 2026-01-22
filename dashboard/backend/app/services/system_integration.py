"""
Integration with main Self-Adaptive System
Provides access to trained models, historical data, and system state
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SystemIntegration:
    """Provides integration with the main self-adaptive system"""
    
    def __init__(self, project_root: str = None):
        """
        Initialize system integration
        
        Args:
            project_root: Path to main project root directory
        """
        if project_root is None:
            # Auto-detect project root (2 levels up from this file)
            project_root = str(Path(__file__).parent.parent.parent.parent.parent)
        
        self.project_root = project_root
        self.data_dir = os.path.join(project_root, 'data')
        self.src_dir = os.path.join(project_root, 'src')
        
        logger.info(f"System Integration initialized at {self.project_root}")
    
    def get_latest_metrics_file(self) -> Optional[str]:
        """Get the path to the most recent metrics JSON file"""
        try:
            if not os.path.exists(self.data_dir):
                return None
            
            metrics_files = [f for f in os.listdir(self.data_dir) if f.startswith('metrics_') and f.endswith('.json')]
            if not metrics_files:
                return None
            
            # Get most recent file
            latest = sorted(metrics_files)[-1]
            return os.path.join(self.data_dir, latest)
        except Exception as e:
            logger.error(f"Error getting latest metrics file: {e}")
            return None
    
    def get_latest_anomalies_file(self) -> Optional[str]:
        """Get the path to the most recent anomalies JSON file"""
        try:
            if not os.path.exists(self.data_dir):
                return None
            
            anomaly_files = [f for f in os.listdir(self.data_dir) if f.startswith('anomalies_') and f.endswith('.json')]
            if not anomaly_files:
                return None
            
            latest = sorted(anomaly_files)[-1]
            return os.path.join(self.data_dir, latest)
        except Exception as e:
            logger.error(f"Error getting latest anomalies file: {e}")
            return None
    
    def get_latest_decisions_file(self) -> Optional[str]:
        """Get the path to the most recent decisions JSON file"""
        try:
            if not os.path.exists(self.data_dir):
                return None
            
            decision_files = [f for f in os.listdir(self.data_dir) if f.startswith('decisions_') and f.endswith('.json')]
            if not decision_files:
                return None
            
            latest = sorted(decision_files)[-1]
            return os.path.join(self.data_dir, latest)
        except Exception as e:
            logger.error(f"Error getting latest decisions file: {e}")
            return None
    
    def load_metrics_history(self, limit: int = 100) -> List[Dict]:
        """
        Load historical metrics from JSON file
        
        Args:
            limit: Maximum number of recent metrics to load
            
        Returns:
            List of metric dictionaries
        """
        try:
            metrics_file = self.get_latest_metrics_file()
            if not metrics_file:
                logger.warning("No metrics file found")
                return []
            
            with open(metrics_file, 'r', encoding='utf-8') as f:
                all_metrics = json.load(f)
            
            # Return only the most recent ones
            return all_metrics[-limit:] if limit else all_metrics
        except Exception as e:
            logger.error(f"Error loading metrics history: {e}")
            return []
    
    def load_anomalies_history(self, limit: int = 50) -> List[Dict]:
        """
        Load historical anomalies from JSON file
        
        Args:
            limit: Maximum number of recent anomalies to load
            
        Returns:
            List of anomaly detection records
        """
        try:
            anomalies_file = self.get_latest_anomalies_file()
            if not anomalies_file:
                logger.warning("No anomalies file found")
                return []
            
            with open(anomalies_file, 'r', encoding='utf-8') as f:
                all_anomalies = json.load(f)
            
            return all_anomalies[-limit:] if limit else all_anomalies
        except Exception as e:
            logger.error(f"Error loading anomalies history: {e}")
            return []
    
    def load_decisions_history(self, limit: int = 50) -> List[Dict]:
        """
        Load historical decisions from JSON file
        
        Args:
            limit: Maximum number of recent decisions to load
            
        Returns:
            List of decision records
        """
        try:
            decisions_file = self.get_latest_decisions_file()
            if not decisions_file:
                logger.warning("No decisions file found")
                return []
            
            with open(decisions_file, 'r', encoding='utf-8') as f:
                all_decisions = json.load(f)
            
            return all_decisions[-limit:] if limit else all_decisions
        except Exception as e:
            logger.error(f"Error loading decisions history: {e}")
            return []
    
    def get_system_summary(self) -> Dict:
        """Get comprehensive system summary including all recent data"""
        try:
            metrics = self.load_metrics_history(limit=10)
            anomalies = self.load_anomalies_history(limit=10)
            decisions = self.load_decisions_history(limit=10)
            
            # Calculate statistics
            if metrics:
                latest_metric = metrics[-1]
                cpu_values = [m.get('cpu_percent', 0) for m in metrics]
                memory_values = [m.get('memory_percent', 0) for m in metrics]
                
                summary = {
                    'status': 'operational',
                    'timestamp': datetime.utcnow().isoformat(),
                    'last_updated': latest_metric.get('timestamp'),
                    'metrics': {
                        'latest': latest_metric,
                        'total_samples': len(self.load_metrics_history(limit=None)),
                        'cpu': {
                            'current': latest_metric.get('cpu_percent', 0),
                            'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                            'max': max(cpu_values) if cpu_values else 0,
                            'min': min(cpu_values) if cpu_values else 0
                        },
                        'memory': {
                            'current': latest_metric.get('memory_percent', 0),
                            'average': sum(memory_values) / len(memory_values) if memory_values else 0,
                            'max': max(memory_values) if memory_values else 0,
                            'min': min(memory_values) if memory_values else 0
                        }
                    },
                    'anomalies': {
                        'recent': anomalies,
                        'total_detected': len(self.load_anomalies_history(limit=None)),
                        'detection_rate': len(anomalies) / max(len(metrics), 1) if metrics else 0
                    },
                    'decisions': {
                        'recent': decisions,
                        'total_made': len(self.load_decisions_history(limit=None))
                    }
                }
            else:
                summary = {
                    'status': 'no_data',
                    'timestamp': datetime.utcnow().isoformat(),
                    'message': 'No metrics data available. Run the main system first.'
                }
            
            return summary
        except Exception as e:
            logger.error(f"Error generating system summary: {e}")
            return {
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def get_health_status(self) -> Dict:
        """Get overall health status based on recent data"""
        try:
            metrics = self.load_metrics_history(limit=5)
            anomalies = self.load_anomalies_history(limit=10)
            
            if not metrics:
                return {
                    'status': 'unknown',
                    'health_score': 0,
                    'message': 'No data available'
                }
            
            latest = metrics[-1]
            cpu = latest.get('cpu_percent', 0)
            memory = latest.get('memory_percent', 0)
            
            # Calculate health score (0-100)
            cpu_score = max(0, 100 - cpu)
            memory_score = max(0, 100 - memory)
            
            # Penalize for anomalies
            anomaly_penalty = min(20, len(anomalies) * 2)
            
            health_score = (cpu_score + memory_score) / 2 - anomaly_penalty
            health_score = max(0, min(100, health_score))
            
            # Determine status
            if health_score >= 80:
                status = 'healthy'
            elif health_score >= 50:
                status = 'warning'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'health_score': round(health_score, 1),
                'cpu_usage': round(cpu, 1),
                'memory_usage': round(memory, 1),
                'recent_anomalies': len(anomalies),
                'last_check': latest.get('timestamp')
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'status': 'error',
                'health_score': 0,
                'error': str(e)
            }


# Global instance
_system_integration = None


def get_system_integration(project_root: str = None) -> SystemIntegration:
    """Get or create the global system integration instance"""
    global _system_integration
    if _system_integration is None:
        _system_integration = SystemIntegration(project_root)
    return _system_integration
