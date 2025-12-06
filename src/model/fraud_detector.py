"""
Fraud detection model for scoring transactions
"""
import logging
import os
from typing import Dict, Tuple, Optional
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class FraudDetector:
    """
    Machine learning model for detecting fraudulent transactions
    """
    
    def __init__(self, config: Dict):
        """
        Initialize fraud detector
        
        Args:
            config: Configuration dictionary with model settings
        """
        self.config = config
        self.model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.threshold = config.get('threshold', 0.7)
        self.model_loaded = False
        
    def load_model(self):
        """Load trained model and scaler from disk"""
        model_path = self.config.get('path', 'models/fraud_detection_model.pkl')
        scaler_path = self.config.get('scaler_path', 'models/scaler.pkl')
        
        try:
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                # Load both model and scaler from files
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                logger.info(f"Loaded model from {model_path}")
                logger.info(f"Loaded scaler from {scaler_path}")
            else:
                # Create default model if files don't exist
                logger.warning(f"Model or scaler files not found, using default model")
                self._create_default_model()
                
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
            self._create_default_model()
            return False
    
    def _create_default_model(self):
        """Create a default model for demonstration purposes"""
        logger.info("Creating default Random Forest model")
        
        # Train on synthetic data for demo
        np.random.seed(42)
        X_synthetic = np.random.randn(1000, 15)
        # Create synthetic labels with fraud probability based on features
        y_synthetic = (X_synthetic[:, 0] > 1.5) | (X_synthetic[:, 13] > 2.0)
        y_synthetic = y_synthetic.astype(int)
        
        # Fit scaler first
        self.scaler = StandardScaler()
        self.scaler.fit(X_synthetic)
        X_scaled = self.scaler.transform(X_synthetic)
        
        # Then train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_scaled, y_synthetic)
        
        self.model_loaded = True
        logger.info("Default model created and trained on synthetic data")
    
    def predict(self, features: np.ndarray) -> Tuple[int, float]:
        """
        Predict if transaction is fraudulent
        
        Args:
            features: Feature vector for transaction
            
        Returns:
            Tuple of (prediction, fraud_probability)
        """
        if not self.model_loaded:
            self.load_model()
        
        # Ensure features is 2D array
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Scale features
        if self.scaler:
            features = self.scaler.transform(features)
        
        # Get prediction and probability
        fraud_prob = self.model.predict_proba(features)[0][1]
        prediction = 1 if fraud_prob >= self.threshold else 0
        
        return prediction, float(fraud_prob)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores from the model
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.model_loaded or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        feature_names = [
            'amount', 'transaction_hour', 'transaction_day', 'merchant_category_code',
            'is_weekend', 'is_night', 'user_total_transactions', 'user_avg_amount',
            'user_std_amount', 'velocity_1h', 'velocity_24h', 'amount_1h',
            'amount_24h', 'amount_z_score', 'transaction_type_encoded'
        ]
        
        importances = self.model.feature_importances_
        return dict(zip(feature_names, importances))
    
    def save_model(self, model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        """
        Save model and scaler to disk
        
        Args:
            model_path: Path to save model
            scaler_path: Path to save scaler
        """
        if not self.model_loaded:
            logger.warning("No model loaded to save")
            return False
        
        model_path = model_path or self.config.get('path', 'models/fraud_detection_model.pkl')
        scaler_path = scaler_path or self.config.get('scaler_path', 'models/scaler.pkl')
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"Model saved to {model_path}")
            logger.info(f"Scaler saved to {scaler_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}", exc_info=True)
            return False
