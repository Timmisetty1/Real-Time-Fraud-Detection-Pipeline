"""
REST API for fraud detection service
"""
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import yaml
import numpy as np

from feature_engineering.feature_extractor import FeatureExtractor
from model.fraud_detector import FraudDetector
from scoring.scoring_service import ScoringService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global components
feature_extractor = None
fraud_detector = None
scoring_service = None


def initialize_components(config_path: str = 'config/config.yaml'):
    """Initialize pipeline components"""
    global feature_extractor, fraud_detector, scoring_service
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Failed to load config: {e}, using defaults")
        config = {
            'features': {},
            'model': {'threshold': 0.7}
        }
    
    feature_extractor = FeatureExtractor(config.get('features', {}))
    fraud_detector = FraudDetector(config.get('model', {}))
    fraud_detector.load_model()
    scoring_service = ScoringService(feature_extractor, fraud_detector)
    
    logger.info("API components initialized")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': fraud_detector.model_loaded if fraud_detector else False
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict fraud for a single transaction
    
    Expected JSON body:
    {
        "transaction_id": "tx123",
        "user_id": "user456",
        "amount": 150.50,
        "merchant_name": "Amazon",
        "merchant_category_code": 5411,
        "transaction_type": "purchase",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    """
    try:
        transaction = request.get_json()
        
        if not transaction:
            return jsonify({'error': 'No transaction data provided'}), 400
        
        # Validate required fields
        required_fields = ['transaction_id', 'user_id', 'amount']
        missing_fields = [f for f in required_fields if f not in transaction]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {missing_fields}'
            }), 400
        
        # Score transaction
        result = scoring_service.score_transaction(transaction)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """
    Predict fraud for multiple transactions
    
    Expected JSON body:
    {
        "transactions": [...]
    }
    """
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        if not transactions:
            return jsonify({'error': 'No transactions provided'}), 400
        
        results = []
        for transaction in transactions:
            result = scoring_service.score_transaction(transaction)
            results.append(result)
        
        return jsonify({
            'results': results,
            'total': len(results),
            'fraud_count': sum(1 for r in results if r.get('is_fraud', False))
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/statistics', methods=['GET'])
def statistics():
    """Get scoring statistics"""
    try:
        stats = scoring_service.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Statistics error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/feature_importance', methods=['GET'])
def feature_importance():
    """Get model feature importance"""
    try:
        importance = fraud_detector.get_feature_importance()
        return jsonify(importance), 200
    except Exception as e:
        logger.error(f"Feature importance error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/reset_statistics', methods=['POST'])
def reset_statistics():
    """Reset statistics counters"""
    try:
        scoring_service.reset_statistics()
        return jsonify({'message': 'Statistics reset successfully'}), 200
    except Exception as e:
        logger.error(f"Reset statistics error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def main():
    """Main entry point for API server"""
    initialize_components()
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )


if __name__ == '__main__':
    main()
