"""
Anomaly Detection Module
Implements Isolation Forest-based anomaly detection
Detects resource anomalies in real-time
"""

import numpy as np
import pickle
import logging
from typing import Dict, Tuple, List, Optional
from sklearn.ensemble import IsolationForest
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detects anomalies using Isolation Forest algorithm
    Suitable for high-dimensional unsupervised anomaly detection
    """
    
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        """
        Initialize AnomalyDetector
        
        Args:
            contamination: Expected proportion of anomalies (0.01 to 0.5)
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
            max_samples='auto',
            max_features=1.0,
            bootstrap=False,
            n_jobs=-1
        )
        self.is_trained = False
        self.training_samples = 0
        self.anomaly_threshold = None
    
    def train(self, X: np.ndarray) -> None:
        """
        Train the anomaly detection model
        
        Args:
            X: Feature matrix (samples x features)
        """
        logger.info(f"Training Isolation Forest with {len(X)} samples")
        self.model.fit(X)
        self.is_trained = True
        self.training_samples = len(X)
        
        # Get anomaly scores for threshold
        scores = self.model.score_samples(X)
        self.anomaly_threshold = np.percentile(scores, 100 * self.contamination)
        
        logger.info(f"Model trained. Anomaly threshold: {self.anomaly_threshold:.4f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomalies
        
        Args:
            X: Feature matrix
            
        Returns:
            Array of predictions: 1 for normal, -1 for anomaly
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get anomaly scores and normalized probabilities
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (anomaly_scores, anomaly_probabilities)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        scores = self.model.score_samples(X)
        
        # Normalize scores to [0, 1] probability
        # Lower scores = more anomalous
        min_score = np.min(scores)
        max_score = np.max(scores)
        
        if max_score == min_score:
            probabilities = np.zeros_like(scores)
        else:
            # Invert and normalize: high anomaly score -> high probability
            probabilities = 1 - (scores - min_score) / (max_score - min_score)
        
        return scores, probabilities
    
    def predict_single(self, x: np.ndarray) -> Tuple[int, float, float]:
        """
        Predict anomaly for a single sample
        
        Args:
            x: Single feature vector (1D array)
            
        Returns:
            Tuple of (prediction, anomaly_score, probability)
        """
        x_reshaped = x.reshape(1, -1)
        prediction = self.predict(x_reshaped)[0]
        score, prob = self.predict_proba(x_reshaped)
        
        return int(prediction), float(score[0]), float(prob[0])
    
    def save_model(self, filepath: str) -> None:
        """Save trained model to file"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load trained model from file"""
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")


class AnomalyAnalyzer:
    """
    Analyzes anomalies and provides detailed insights
    """
    
    def __init__(self, detector: AnomalyDetector, feature_names: List[str]):
        """
        Initialize AnomalyAnalyzer
        
        Args:
            detector: Trained AnomalyDetector instance
            feature_names: List of feature names
        """
        self.detector = detector
        self.feature_names = feature_names
        self.anomaly_log = []
    
    def analyze_sample(self, x: np.ndarray, metadata: Optional[Dict] = None) -> Dict:
        """
        Comprehensive anomaly analysis for a single sample
        
        Args:
            x: Feature vector
            metadata: Optional metadata (e.g., timestamp)
            
        Returns:
            Detailed analysis dictionary
        """
        prediction, score, probability = self.detector.predict_single(x)
        
        analysis = {
            'prediction': prediction,
            'is_anomaly': prediction == -1,
            'anomaly_score': score,
            'anomaly_probability': probability,
            'timestamp': metadata.get('timestamp') if metadata else datetime.now().isoformat(),
            'feature_values': {}
        }
        
        # Add feature values
        for i, name in enumerate(self.feature_names):
            analysis['feature_values'][name] = float(x[i])
        
        # Identify most anomalous features
        if analysis['is_anomaly']:
            analysis['contributing_features'] = self._identify_anomalous_features(x)
        
        # Store in log
        self.anomaly_log.append(analysis)
        
        return analysis
    
    def _identify_anomalous_features(self, x: np.ndarray, top_n: int = 5) -> List[str]:
        """
        Identify features most contributing to anomaly
        Uses absolute feature values as proxy
        
        Args:
            x: Feature vector
            top_n: Number of top features to return
            
        Returns:
            List of feature names sorted by contribution
        """
        # Use absolute feature values as importance measure
        importance = np.abs(x)
        top_indices = np.argsort(importance)[-top_n:][::-1]
        
        return [self.feature_names[i] for i in top_indices]
    
    def get_anomaly_statistics(self) -> Dict:
        """Get statistics about detected anomalies"""
        if not self.anomaly_log:
            return {
                'total_samples': 0,
                'anomalies_detected': 0,
                'anomaly_rate': 0.0,
                'average_anomaly_score': 0.0,
                'average_anomaly_probability': 0.0
            }
        
        anomalies = [a for a in self.anomaly_log if a['is_anomaly']]
        
        return {
            'total_samples': len(self.anomaly_log),
            'anomalies_detected': len(anomalies),
            'anomaly_rate': len(anomalies) / len(self.anomaly_log) if self.anomaly_log else 0,
            'average_anomaly_score': float(np.mean([a['anomaly_score'] for a in self.anomaly_log])),
            'average_anomaly_probability': float(np.mean([a['anomaly_probability'] for a in self.anomaly_log]))
        }
    
    def get_recent_anomalies(self, limit: int = 10) -> List[Dict]:
        """Get recent anomalies"""
        anomalies = [a for a in self.anomaly_log if a['is_anomaly']]
        return anomalies[-limit:]
    
    def export_anomaly_log(self, filepath: str) -> None:
        """Export anomaly log to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.anomaly_log, f, indent=2, default=str)
        logger.info(f"Anomaly log exported to {filepath}")


class EnsembleAnomalyDetector:
    """
    Ensemble approach combining multiple anomaly detection methods
    """
    
    def __init__(self, contamination: float = 0.05):
        """Initialize ensemble detector"""
        self.isolation_forest = AnomalyDetector(contamination=contamination)
        self.trained = False
    
    def train(self, X: np.ndarray) -> None:
        """Train all base models"""
        self.isolation_forest.train(X)
        self.trained = True
        logger.info("Ensemble model trained")
    
    def predict(self, X: np.ndarray, voting_threshold: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict using ensemble voting
        
        Args:
            X: Feature matrix
            voting_threshold: Threshold for anomaly probability
            
        Returns:
            Tuple of (predictions, probabilities)
        """
        if not self.trained:
            raise ValueError("Ensemble must be trained before prediction")
        
        # Get predictions from isolation forest
        if_scores, if_probs = self.isolation_forest.predict_proba(X)
        
        # Use isolation forest as primary detector
        predictions = np.where(if_probs >= voting_threshold, -1, 1)
        
        return predictions, if_probs
    
    def predict_single(self, x: np.ndarray) -> Tuple[int, float]:
        """Predict single sample"""
        predictions, probs = self.predict(x.reshape(1, -1))
        return int(predictions[0]), float(probs[0])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    np.random.seed(42)
    X_normal = np.random.normal(0, 1, (1000, 20))
    X_anomaly = np.random.uniform(-4, 4, (50, 20))
    X_train = np.vstack([X_normal, X_anomaly])
    
    # Train detector
    detector = AnomalyDetector(contamination=0.05)
    detector.train(X_train)
    
    # Test on new data
    X_test = np.random.normal(0, 1, (100, 20))
    X_test[0] = np.random.uniform(-4, 4, 20)  # Add one anomaly
    
    predictions = detector.predict(X_test)
    print(f"Predictions shape: {predictions.shape}")
    print(f"Anomalies detected: {np.sum(predictions == -1)}")
