"""
Feature extraction and engineering for fraud detection
"""
import logging
from datetime import datetime
from typing import Dict, List
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extract and engineer features from transaction data
    """
    
    def __init__(self, config: Dict):
        """
        Initialize feature extractor
        
        Args:
            config: Configuration dictionary with feature settings
        """
        self.config = config
        self.numerical_features = config.get('numerical', [])
        self.categorical_features = config.get('categorical', [])
        
        # In-memory storage for velocity calculations (in production, use Redis)
        self.transaction_history = defaultdict(lambda: deque(maxlen=1000))
        self.user_stats = defaultdict(lambda: {
            'total_transactions': 0,
            'total_amount': 0.0,
            'avg_amount': 0.0,
            'std_amount': 0.0
        })
    
    def extract_features(self, transaction: Dict) -> Dict:
        """
        Extract features from a transaction
        
        Args:
            transaction: Raw transaction data
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Basic features
        features['amount'] = float(transaction.get('amount', 0))
        features['transaction_type'] = transaction.get('transaction_type', 'unknown')
        features['merchant_name'] = transaction.get('merchant_name', 'unknown')
        features['merchant_category_code'] = int(transaction.get('merchant_category_code', 0))
        
        # Temporal features
        timestamp = transaction.get('timestamp', datetime.now().isoformat())
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        features['transaction_hour'] = dt.hour
        features['transaction_day'] = dt.weekday()
        features['is_weekend'] = 1 if dt.weekday() >= 5 else 0
        features['is_night'] = 1 if dt.hour >= 22 or dt.hour <= 6 else 0
        
        # User-based features
        user_id = transaction.get('user_id', 'unknown')
        features.update(self._extract_user_features(user_id, features['amount'], timestamp))
        
        # Velocity features
        features.update(self._calculate_velocity(user_id, timestamp, features['amount']))
        
        # Derived features
        features['amount_z_score'] = self._calculate_z_score(
            features['amount'],
            features['user_avg_amount'],
            features['user_std_amount']
        )
        
        # Categorical encoding (simple label encoding for demo)
        features['transaction_type_encoded'] = self._encode_category(
            features['transaction_type'],
            ['purchase', 'withdrawal', 'transfer', 'payment']
        )
        
        return features
    
    def _extract_user_features(self, user_id: str, amount: float, timestamp: str) -> Dict:
        """Extract user-specific historical features"""
        stats = self.user_stats[user_id]
        
        # Update statistics
        stats['total_transactions'] += 1
        stats['total_amount'] += amount
        stats['avg_amount'] = stats['total_amount'] / stats['total_transactions']
        
        # Calculate standard deviation
        if stats['total_transactions'] > 1:
            # Simplified std calculation
            stats['std_amount'] = max(stats['avg_amount'] * 0.3, 10.0)
        
        return {
            'user_total_transactions': stats['total_transactions'],
            'user_avg_amount': stats['avg_amount'],
            'user_std_amount': stats['std_amount']
        }
    
    def _calculate_velocity(self, user_id: str, timestamp: str, amount: float) -> Dict:
        """Calculate transaction velocity features"""
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        history = self.transaction_history[user_id]
        
        # Add current transaction
        history.append({
            'timestamp': dt,
            'amount': amount
        })
        
        # Calculate velocity
        now = dt
        count_1h = sum(1 for t in history if (now - t['timestamp']).total_seconds() <= 3600)
        count_24h = sum(1 for t in history if (now - t['timestamp']).total_seconds() <= 86400)
        
        amount_1h = sum(t['amount'] for t in history if (now - t['timestamp']).total_seconds() <= 3600)
        amount_24h = sum(t['amount'] for t in history if (now - t['timestamp']).total_seconds() <= 86400)
        
        return {
            'velocity_1h': count_1h,
            'velocity_24h': count_24h,
            'amount_1h': amount_1h,
            'amount_24h': amount_24h
        }
    
    def _calculate_z_score(self, value: float, mean: float, std: float) -> float:
        """Calculate z-score for anomaly detection"""
        if std == 0 or mean == 0:
            return 0.0
        return (value - mean) / std
    
    def _encode_category(self, value: str, categories: List[str]) -> int:
        """Simple label encoding for categorical features"""
        try:
            return categories.index(value)
        except ValueError:
            return len(categories)  # Unknown category
    
    def get_feature_vector(self, features: Dict) -> List[float]:
        """
        Convert feature dictionary to vector for model input
        
        Args:
            features: Dictionary of features
            
        Returns:
            List of feature values in consistent order
        """
        feature_names = [
            'amount', 'transaction_hour', 'transaction_day', 'merchant_category_code',
            'is_weekend', 'is_night', 'user_total_transactions', 'user_avg_amount',
            'user_std_amount', 'velocity_1h', 'velocity_24h', 'amount_1h',
            'amount_24h', 'amount_z_score', 'transaction_type_encoded'
        ]
        
        return [features.get(name, 0.0) for name in feature_names]
