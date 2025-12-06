"""
Tests for feature extraction
"""
import pytest
from datetime import datetime
from src.feature_engineering.feature_extractor import FeatureExtractor


class TestFeatureExtractor:
    """Test feature extraction functionality"""
    
    @pytest.fixture
    def extractor(self):
        """Create feature extractor instance"""
        config = {
            'numerical': ['amount', 'transaction_hour'],
            'categorical': ['transaction_type', 'merchant_name']
        }
        return FeatureExtractor(config)
    
    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction data"""
        return {
            'transaction_id': 'tx123',
            'user_id': 'user456',
            'amount': 150.50,
            'merchant_name': 'Amazon',
            'merchant_category_code': 5999,
            'transaction_type': 'purchase',
            'timestamp': '2024-01-01T14:30:00'
        }
    
    def test_extract_features(self, extractor, sample_transaction):
        """Test basic feature extraction"""
        features = extractor.extract_features(sample_transaction)
        
        assert 'amount' in features
        assert features['amount'] == 150.50
        assert 'merchant_name' in features
        assert features['merchant_name'] == 'Amazon'
        assert 'transaction_hour' in features
        assert features['transaction_hour'] == 14
    
    def test_temporal_features(self, extractor, sample_transaction):
        """Test temporal feature extraction"""
        features = extractor.extract_features(sample_transaction)
        
        assert 'transaction_hour' in features
        assert 'transaction_day' in features
        assert 'is_weekend' in features
        assert 'is_night' in features
        assert isinstance(features['is_weekend'], int)
    
    def test_user_features(self, extractor, sample_transaction):
        """Test user-based features"""
        features = extractor.extract_features(sample_transaction)
        
        assert 'user_total_transactions' in features
        assert 'user_avg_amount' in features
        assert 'user_std_amount' in features
        assert features['user_total_transactions'] > 0
    
    def test_velocity_features(self, extractor, sample_transaction):
        """Test velocity calculations"""
        # Process multiple transactions
        for i in range(3):
            features = extractor.extract_features(sample_transaction)
        
        assert 'velocity_1h' in features
        assert 'velocity_24h' in features
        assert 'amount_1h' in features
        assert 'amount_24h' in features
        assert features['velocity_1h'] >= 1
    
    def test_feature_vector(self, extractor, sample_transaction):
        """Test feature vector generation"""
        features = extractor.extract_features(sample_transaction)
        vector = extractor.get_feature_vector(features)
        
        assert isinstance(vector, list)
        assert len(vector) == 15
        assert all(isinstance(x, (int, float)) for x in vector)
    
    def test_z_score_calculation(self, extractor):
        """Test z-score calculation"""
        z_score = extractor._calculate_z_score(150.0, 100.0, 25.0)
        assert abs(z_score - 2.0) < 0.01
        
        # Test with zero std
        z_score = extractor._calculate_z_score(150.0, 100.0, 0.0)
        assert z_score == 0.0
    
    def test_category_encoding(self, extractor):
        """Test categorical encoding"""
        categories = ['purchase', 'withdrawal', 'transfer']
        
        encoded = extractor._encode_category('purchase', categories)
        assert encoded == 0
        
        encoded = extractor._encode_category('withdrawal', categories)
        assert encoded == 1
        
        # Unknown category
        encoded = extractor._encode_category('unknown', categories)
        assert encoded == len(categories)
