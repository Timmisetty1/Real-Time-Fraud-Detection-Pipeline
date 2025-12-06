"""
Script to test the fraud detection API
"""
import requests
import json
from datetime import datetime


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get('http://localhost:5000/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_single_prediction():
    """Test single transaction prediction"""
    print("Testing single prediction...")
    
    transaction = {
        'transaction_id': 'tx_test_001',
        'user_id': 'user_test_123',
        'amount': 1500.00,
        'merchant_name': 'Amazon',
        'merchant_category_code': 5999,
        'transaction_type': 'purchase',
        'timestamp': datetime.now().isoformat()
    }
    
    response = requests.post(
        'http://localhost:5000/predict',
        json=transaction,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_batch_prediction():
    """Test batch prediction"""
    print("Testing batch prediction...")
    
    transactions = {
        'transactions': [
            {
                'transaction_id': f'tx_batch_{i}',
                'user_id': 'user_batch_test',
                'amount': 100.0 * (i + 1),
                'merchant_name': 'Store',
                'merchant_category_code': 5411,
                'transaction_type': 'purchase',
                'timestamp': datetime.now().isoformat()
            }
            for i in range(5)
        ]
    }
    
    response = requests.post(
        'http://localhost:5000/batch_predict',
        json=transactions,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_statistics():
    """Test statistics endpoint"""
    print("Testing statistics endpoint...")
    response = requests.get('http://localhost:5000/statistics')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_feature_importance():
    """Test feature importance endpoint"""
    print("Testing feature importance endpoint...")
    response = requests.get('http://localhost:5000/feature_importance')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def main():
    """Run all tests"""
    print("=" * 50)
    print("Fraud Detection API Tests")
    print("=" * 50 + "\n")
    
    try:
        test_health()
        test_single_prediction()
        test_batch_prediction()
        test_statistics()
        test_feature_importance()
        
        print("=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Make sure the API server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
