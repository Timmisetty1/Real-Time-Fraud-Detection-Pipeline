"""
Real-time scoring service for fraud detection
"""
import logging
from typing import Dict
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class ScoringService:
    """
    Real-time scoring service that orchestrates feature extraction and model prediction
    """
    
    def __init__(self, feature_extractor, fraud_detector, alert_producer=None):
        """
        Initialize scoring service
        
        Args:
            feature_extractor: FeatureExtractor instance
            fraud_detector: FraudDetector instance
            alert_producer: AlertProducer instance (optional)
        """
        self.feature_extractor = feature_extractor
        self.fraud_detector = fraud_detector
        self.alert_producer = alert_producer
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'total_fraud': 0,
            'total_legitimate': 0
        }
    
    def score_transaction(self, transaction: Dict) -> Dict:
        """
        Score a transaction for fraud
        
        Args:
            transaction: Raw transaction data
            
        Returns:
            Scoring results with prediction and metadata
        """
        try:
            # Extract features
            features = self.feature_extractor.extract_features(transaction)
            feature_vector = self.feature_extractor.get_feature_vector(features)
            
            # Convert to numpy array
            feature_array = np.array(feature_vector)
            
            # Get prediction
            prediction, fraud_probability = self.fraud_detector.predict(feature_array)
            
            # Update statistics
            self.stats['total_processed'] += 1
            if prediction == 1:
                self.stats['total_fraud'] += 1
            else:
                self.stats['total_legitimate'] += 1
            
            # Create result
            result = {
                'transaction_id': transaction.get('transaction_id', 'unknown'),
                'user_id': transaction.get('user_id', 'unknown'),
                'amount': transaction.get('amount', 0),
                'timestamp': transaction.get('timestamp', datetime.now().isoformat()),
                'is_fraud': bool(prediction),
                'fraud_probability': round(fraud_probability, 4),
                'features': features,
                'scoring_timestamp': datetime.now().isoformat()
            }
            
            # Send alert if fraud detected
            if prediction == 1 and self.alert_producer:
                self._send_alert(result)
            
            logger.info(
                f"Transaction {result['transaction_id']}: "
                f"Fraud={'YES' if prediction == 1 else 'NO'} "
                f"(probability={fraud_probability:.4f})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error scoring transaction: {e}", exc_info=True)
            # Update error statistics but don't count as processed
            result = {
                'transaction_id': transaction.get('transaction_id', 'unknown'),
                'error': str(e),
                'is_fraud': False,
                'fraud_probability': 0.0
            }
            return result
    
    def _send_alert(self, result: Dict):
        """Send fraud alert"""
        try:
            alert = {
                'alert_id': f"alert_{result['transaction_id']}_{datetime.now().timestamp()}",
                'transaction_id': result['transaction_id'],
                'user_id': result['user_id'],
                'amount': result['amount'],
                'fraud_probability': result['fraud_probability'],
                'timestamp': result['scoring_timestamp'],
                'alert_type': 'FRAUD_DETECTED',
                'severity': 'HIGH' if result['fraud_probability'] > 0.9 else 'MEDIUM'
            }
            self.alert_producer.send_alert(alert)
            logger.info(f"Alert sent for transaction {result['transaction_id']}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}", exc_info=True)
    
    def get_statistics(self) -> Dict:
        """Get scoring statistics"""
        fraud_rate = 0.0
        if self.stats['total_processed'] > 0:
            fraud_rate = self.stats['total_fraud'] / self.stats['total_processed']
        
        return {
            **self.stats,
            'fraud_rate': round(fraud_rate, 4)
        }
    
    def reset_statistics(self):
        """Reset statistics counters"""
        self.stats = {
            'total_processed': 0,
            'total_fraud': 0,
            'total_legitimate': 0
        }
