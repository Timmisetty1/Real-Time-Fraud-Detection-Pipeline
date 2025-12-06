"""
Tests for scoring service
"""
import pytest
from src.feature_engineering.feature_extractor import FeatureExtractor
from src.model.fraud_detector import FraudDetector
from src.scoring.scoring_service import ScoringService


class TestScoringService:
    """Test scoring service"""
    
    @pytest.fixture
    def scoring_service(self):
        """Create scoring service instance"""
        feature_extractor = FeatureExtractor({})
        fraud_detector = FraudDetector({'threshold': 0.7})
        fraud_detector.load_model()
        
        return ScoringService(feature_extractor, fraud_detector)
    
    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction"""
        return {
            'transaction_id': 'tx123',
            'user_id': 'user456',
            'amount': 150.50,
            'merchant_name': 'Amazon',
            'merchant_category_code': 5999,
            'transaction_type': 'purchase',
            'timestamp': '2024-01-01T14:30:00'
        }
    
    def test_score_transaction(self, scoring_service, sample_transaction):
        """Test transaction scoring"""
        result = scoring_service.score_transaction(sample_transaction)
        
        assert 'transaction_id' in result
        assert 'is_fraud' in result
        assert 'fraud_probability' in result
        assert result['transaction_id'] == 'tx123'
        assert isinstance(result['is_fraud'], bool)
        assert 0.0 <= result['fraud_probability'] <= 1.0
    
    def test_statistics_tracking(self, scoring_service, sample_transaction):
        """Test statistics are tracked correctly"""
        initial_stats = scoring_service.get_statistics()
        assert initial_stats['total_processed'] == 0
        
        scoring_service.score_transaction(sample_transaction)
        scoring_service.score_transaction(sample_transaction)
        
        stats = scoring_service.get_statistics()
        assert stats['total_processed'] == 2
        assert stats['total_fraud'] + stats['total_legitimate'] == 2
    
    def test_fraud_rate_calculation(self, scoring_service):
        """Test fraud rate calculation"""
        # Create transactions
        normal_tx = {
            'transaction_id': 'tx1',
            'user_id': 'user1',
            'amount': 50.0,
            'merchant_name': 'Coffee Shop',
            'merchant_category_code': 5814,
            'transaction_type': 'purchase',
            'timestamp': '2024-01-01T14:30:00'
        }
        
        for i in range(10):
            scoring_service.score_transaction(normal_tx)
        
        stats = scoring_service.get_statistics()
        assert 'fraud_rate' in stats
        assert 0.0 <= stats['fraud_rate'] <= 1.0
    
    def test_reset_statistics(self, scoring_service, sample_transaction):
        """Test statistics reset"""
        scoring_service.score_transaction(sample_transaction)
        
        stats = scoring_service.get_statistics()
        assert stats['total_processed'] > 0
        
        scoring_service.reset_statistics()
        
        stats = scoring_service.get_statistics()
        assert stats['total_processed'] == 0
        assert stats['total_fraud'] == 0
        assert stats['total_legitimate'] == 0
    
    def test_error_handling(self, scoring_service):
        """Test error handling in scoring"""
        invalid_transaction = {}
        
        result = scoring_service.score_transaction(invalid_transaction)
        
        # Should not crash, should return result with error or default values
        assert 'transaction_id' in result
        assert 'is_fraud' in result
