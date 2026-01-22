"""
Data Preprocessing Module
Prepares monitoring data for ML anomaly detection
Handles normalization, feature extraction, and data quality
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Preprocesses raw monitoring metrics for anomaly detection
    Handles normalization, feature engineering, and cleaning
    """
    
    def __init__(self, scaler_type: str = 'standard'):
        """
        Initialize DataPreprocessor
        
        Args:
            scaler_type: 'standard' (StandardScaler) or 'minmax' (MinMaxScaler)
        """
        if scaler_type == 'standard':
            self.scaler = StandardScaler()
        else:
            self.scaler = MinMaxScaler()
        
        self.is_fitted = False
        self.feature_names = []
    
    def metrics_to_dataframe(self, metrics_list: List[Dict]) -> pd.DataFrame:
        """
        Convert metrics list to pandas DataFrame with flattened features
        
        Args:
            metrics_list: List of metric dictionaries from ResourceMonitor
            
        Returns:
            DataFrame with extracted features
        """
        rows = []
        
        for metric in metrics_list:
            try:
                row = {
                    'timestamp': metric['timestamp'],
                    'cpu_percent': metric['cpu']['percent'],
                    'memory_percent': metric['memory']['percent'],
                    'memory_used_mb': metric['memory']['used_mb'],
                    'disk_percent': metric['disk']['percent'],
                    'disk_used_gb': metric['disk']['used_gb'],
                    'network_bytes_sent_sec': metric['network']['bytes_sent_per_sec'],
                    'network_bytes_recv_sec': metric['network']['bytes_recv_per_sec'],
                    'cpu_frequency': metric['cpu']['frequency_mhz'] or 0,
                }
                rows.append(row)
            except KeyError as e:
                logger.warning(f"Missing key {e} in metric, skipping")
                continue
        
        df = pd.DataFrame(rows)
        return df
    
    def extract_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Extract and engineer features from raw metrics
        
        Args:
            df: DataFrame with raw metrics
            
        Returns:
            DataFrame with engineered features and list of feature names
        """
        df = df.copy()
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        
        # Rolling statistics (moving averages)
        window = 5
        for col in ['cpu_percent', 'memory_percent', 'disk_percent']:
            df[f'{col}_ma5'] = df[col].rolling(window=window, min_periods=1).mean()
            df[f'{col}_ma10'] = df[col].rolling(window=10, min_periods=1).mean()
            df[f'{col}_std5'] = df[col].rolling(window=window, min_periods=1).std().fillna(0)
        
        # Rate of change
        df['cpu_roc'] = df['cpu_percent'].diff().fillna(0)
        df['memory_roc'] = df['memory_percent'].diff().fillna(0)
        df['disk_roc'] = df['disk_percent'].diff().fillna(0)
        
        # Composite features
        df['resource_pressure'] = (
            df['cpu_percent'] * 0.3 +
            df['memory_percent'] * 0.4 +
            df['disk_percent'] * 0.3
        )
        
        df['network_activity'] = (
            df['network_bytes_sent_sec'] + df['network_bytes_recv_sec']
        )
        
        # Features to use for anomaly detection
        feature_cols = [
            'cpu_percent', 'memory_percent', 'disk_percent',
            'memory_used_mb', 'disk_used_gb',
            'network_bytes_sent_sec', 'network_bytes_recv_sec',
            'cpu_frequency',
            'cpu_percent_ma5', 'memory_percent_ma5', 'disk_percent_ma5',
            'cpu_percent_std5', 'memory_percent_std5', 'disk_percent_std5',
            'cpu_roc', 'memory_roc', 'disk_roc',
            'resource_pressure', 'network_activity',
            'hour', 'minute'
        ]
        
        # Ensure all feature columns exist
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0
        
        self.feature_names = feature_cols
        return df[feature_cols], feature_cols
    
    def normalize_features(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        """
        Normalize features using configured scaler
        
        Args:
            X: Feature matrix (samples x features)
            fit: Whether to fit the scaler on this data
            
        Returns:
            Normalized feature matrix
        """
        if fit:
            X_scaled = self.scaler.fit_transform(X)
            self.is_fitted = True
        else:
            if not self.is_fitted:
                logger.warning("Scaler not fitted, fitting on this data")
                X_scaled = self.scaler.fit_transform(X)
                self.is_fitted = True
            else:
                X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataframe
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame with missing values handled
        """
        df = df.copy()
        
        # Forward fill followed by backward fill
        df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        return df
    
    def remove_outliers_iqr(self, df: pd.DataFrame, columns: List[str], 
                            multiplier: float = 1.5) -> pd.DataFrame:
        """
        Remove outliers using IQR method
        
        Args:
            df: Input dataframe
            columns: Columns to check for outliers
            multiplier: IQR multiplier (1.5 = standard)
            
        Returns:
            DataFrame with outliers removed
        """
        df = df.copy()
        
        for col in columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR
            
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            logger.info(f"Removed outliers from {col}: kept {len(df)} rows")
        
        return df
    
    def prepare_for_training(self, metrics_list: List[Dict], 
                            remove_outliers: bool = True) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Complete preprocessing pipeline
        
        Args:
            metrics_list: Raw metrics from monitoring
            remove_outliers: Whether to remove outliers
            
        Returns:
            Normalized feature matrix and the dataframe
        """
        # Convert to dataframe
        df = self.metrics_to_dataframe(metrics_list)
        logger.info(f"Created dataframe with {len(df)} samples")
        
        # Handle missing values
        df = self.handle_missing_values(df)
        logger.info("Missing values handled")
        
        # Extract features
        df, feature_names = self.extract_features(df)
        logger.info(f"Extracted {len(feature_names)} features")
        
        # Remove outliers if requested
        if remove_outliers:
            df = self.remove_outliers_iqr(df, 
                columns=['cpu_percent', 'memory_percent', 'disk_percent'])
        
        # Normalize
        X = self.normalize_features(df.values, fit=True)
        logger.info("Features normalized")
        
        return X, df
    
    def prepare_inference_features(self, metrics: Dict) -> np.ndarray:
        """
        Prepare a single metric for inference
        
        Args:
            metrics: Single metric dictionary
            
        Returns:
            Feature vector ready for prediction
        """
        # Convert to dataframe
        df = self.metrics_to_dataframe([metrics])
        
        # Extract features
        df, _ = self.extract_features(df)
        
        # Normalize
        X = self.normalize_features(df.values, fit=False)
        
        return X[0]  # Return single sample


class FeatureStatistics:
    """Calculate and store feature statistics for monitoring"""
    
    def __init__(self):
        self.stats = {}
    
    def calculate(self, X: np.ndarray, feature_names: List[str]) -> Dict:
        """
        Calculate statistics for each feature
        
        Args:
            X: Feature matrix
            feature_names: List of feature names
            
        Returns:
            Dictionary with statistics
        """
        for i, name in enumerate(feature_names):
            feature_data = X[:, i]
            self.stats[name] = {
                'mean': float(np.mean(feature_data)),
                'std': float(np.std(feature_data)),
                'min': float(np.min(feature_data)),
                'max': float(np.max(feature_data)),
                'median': float(np.median(feature_data))
            }
        
        return self.stats
    
    def get_stats(self, feature_name: str) -> Optional[Dict]:
        """Get statistics for a specific feature"""
        return self.stats.get(feature_name)


if __name__ == "__main__":
    # Test preprocessing
    logging.basicConfig(level=logging.INFO)
    
    # Create sample metrics
    sample_metrics = [
        {
            'timestamp': datetime.now().isoformat(),
            'cpu': {'percent': 50, 'cores': 4, 'frequency_mhz': 2400},
            'memory': {'total_mb': 8192, 'used_mb': 4096, 'available_mb': 4096, 'percent': 50},
            'disk': {'total_gb': 256, 'used_gb': 128, 'free_gb': 128, 'percent': 50},
            'network': {
                'bytes_sent': 1000000,
                'bytes_recv': 1000000,
                'packets_sent': 1000,
                'packets_recv': 1000,
                'bytes_sent_per_sec': 10000,
                'bytes_recv_per_sec': 10000
            },
            'top_processes': []
        } for _ in range(100)
    ]
    
    preprocessor = DataPreprocessor()
    X, df = preprocessor.prepare_for_training(sample_metrics)
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Features: {preprocessor.feature_names}")
