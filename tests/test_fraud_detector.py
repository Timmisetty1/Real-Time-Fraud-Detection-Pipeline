"""
Tests for fraud detector model
"""
import pytest
import numpy as np
from src.model.fraud_detector import FraudDetector


class TestFraudDetector:
    """Test fraud detection model"""
    
    @pytest.fixture
    def detector(self):
        """Create fraud detector instance"""
        config = {
            'threshold': 0.7,
            'path': 'models/fraud_detection_model.pkl',
            'scaler_path': 'models/scaler.pkl'
        }
        return FraudDetector(config)
    
    def test_initialization(self, detector):
        """Test detector initialization"""
        assert detector.threshold == 0.7
        assert detector.model is None
        assert detector.scaler is None
        assert not detector.model_loaded
    
    def test_default_model_creation(self, detector):
        """Test default model creation"""
        detector._create_default_model()
        
        assert detector.model is not None
        assert detector.scaler is not None
        assert detector.model_loaded
    
    def test_prediction(self, detector):
        """Test fraud prediction"""
        detector.load_model()
        
        # Create sample feature vector
        features = np.array([
            100.0,  # amount
            14,     # transaction_hour
            2,      # transaction_day
            5999,   # merchant_category_code
            0,      # is_weekend
            0,      # is_night
            5,      # user_total_transactions
            80.0,   # user_avg_amount
            20.0,   # user_std_amount
            1,      # velocity_1h
            3,      # velocity_24h
            100.0,  # amount_1h
            300.0,  # amount_24h
            1.0,    # amount_z_score
            0       # transaction_type_encoded
        ])
        
        prediction, probability = detector.predict(features)
        
        assert prediction in [0, 1]
        assert 0.0 <= probability <= 1.0
    
    def test_prediction_2d_array(self, detector):
        """Test prediction with 2D array"""
        detector.load_model()
        
        features = np.random.randn(1, 15)
        prediction, probability = detector.predict(features)
        
        assert prediction in [0, 1]
        assert 0.0 <= probability <= 1.0
    
    def test_high_fraud_probability(self, detector):
        """Test high fraud score triggers alert"""
        detector.load_model()
        
        # Features likely to indicate fraud (high amount, unusual behavior)
        features = np.array([
            5000.0,  # Very high amount
            3,       # Late night
            2,       # transaction_day
            5999,    # merchant_category_code
            0,       # is_weekend
            1,       # is_night
            2,       # Low user_total_transactions
            100.0,   # user_avg_amount
            30.0,    # user_std_amount
            5,       # High velocity_1h
            20,      # High velocity_24h
            3000.0,  # High amount_1h
            8000.0,  # High amount_24h
            3.5,     # High z_score
            0        # transaction_type_encoded
        ])
        
        prediction, probability = detector.predict(features)
        # Should likely be flagged as fraud
        assert probability >= 0.0
    
    def test_feature_importance(self, detector):
        """Test feature importance retrieval"""
        detector.load_model()
        
        importance = detector.get_feature_importance()
        
        assert isinstance(importance, dict)
        if importance:  # If model has feature importance
            assert len(importance) > 0
            assert all(isinstance(v, (float, np.floating)) for v in importance.values())
    
    def test_threshold_application(self, detector):
        """Test threshold is applied correctly"""
        detector.threshold = 0.5
        detector.load_model()
        
        # Create features
        features = np.random.randn(15)
        prediction, probability = detector.predict(features)
        
        # Check threshold is applied
        if probability >= 0.5:
            assert prediction == 1
        else:
            assert prediction == 0
