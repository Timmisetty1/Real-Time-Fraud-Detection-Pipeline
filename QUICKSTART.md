# Quick Start Guide

This guide will help you get the fraud detection pipeline up and running in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Docker and Docker Compose (optional, for Kafka)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Timmisetty1/Real-Time-Fraud-Detection-Pipeline.git
cd Real-Time-Fraud-Detection-Pipeline
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Running the API (Standalone Mode)

The easiest way to test the fraud detection system is through the REST API:

### Start the API Server

```bash
cd src
python api.py
```

The API will start on `http://localhost:5000`

### Test with Sample Requests

In a new terminal, test the API:

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Single Transaction Prediction
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx123",
    "user_id": "user456",
    "amount": 150.50,
    "merchant_name": "Amazon",
    "merchant_category_code": 5999,
    "transaction_type": "purchase",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

#### Batch Prediction
```bash
curl -X POST http://localhost:5000/batch_predict \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {
        "transaction_id": "tx001",
        "user_id": "user1",
        "amount": 50.0,
        "merchant_name": "Coffee Shop",
        "merchant_category_code": 5814,
        "transaction_type": "purchase",
        "timestamp": "2024-01-01T09:00:00Z"
      }
    ]
  }'
```

#### Get Statistics
```bash
curl http://localhost:5000/statistics
```

## Running with Kafka (Streaming Mode)

For real-time stream processing:

### 1. Start Kafka Infrastructure

```bash
docker-compose up -d
```

Wait about 30 seconds for Kafka to be ready.

### 2. Start the Pipeline

In one terminal:
```bash
cd src
python pipeline.py
```

### 3. Generate Test Transactions

In another terminal:
```bash
python scripts/generate_transactions.py --num 50 --fraud-rate 0.2 --delay 0.5
```

This will generate 50 transactions with 20% fraud rate, sending one every 0.5 seconds.

### 4. Monitor Results

- Pipeline logs: Check the terminal where you ran `pipeline.py`
- Kafka UI: Open http://localhost:8080 in your browser
- Metrics: http://localhost:8000 (Prometheus metrics)

## Understanding the Output

### Prediction Response

```json
{
  "transaction_id": "tx123",
  "user_id": "user456",
  "amount": 150.50,
  "is_fraud": false,
  "fraud_probability": 0.6778,
  "timestamp": "2024-01-01T12:00:00Z",
  "scoring_timestamp": "2024-01-01T12:00:01Z",
  "features": {
    "amount": 150.50,
    "transaction_hour": 12,
    "velocity_1h": 1,
    "amount_z_score": 1.2
  }
}
```

- **is_fraud**: Boolean indicating if transaction is classified as fraud
- **fraud_probability**: Confidence score (0.0 to 1.0)
- **features**: Extracted features used for prediction

### Fraud Threshold

By default, transactions with `fraud_probability >= 0.7` are marked as fraud. You can adjust this in `config/config.yaml`:

```yaml
model:
  threshold: 0.7
```

## Common Use Cases

### 1. Batch Processing Transactions

```python
import requests

transactions = [
    {"transaction_id": f"tx{i}", "user_id": "user1", "amount": 100 * i, ...}
    for i in range(10)
]

response = requests.post(
    'http://localhost:5000/batch_predict',
    json={'transactions': transactions}
)

print(response.json())
```

### 2. Integration with Your Application

```python
import requests

def check_fraud(transaction_data):
    response = requests.post(
        'http://localhost:5000/predict',
        json=transaction_data,
        timeout=1  # 1 second timeout
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['is_fraud'], result['fraud_probability']
    else:
        # Handle error
        return False, 0.0

# Use in your app
transaction = {
    "transaction_id": "tx001",
    "user_id": "user123",
    "amount": 250.00,
    # ... other fields
}

is_fraud, probability = check_fraud(transaction)
if is_fraud:
    print(f"⚠️  Fraud detected! Probability: {probability:.2%}")
```

### 3. Testing Different Scenarios

```bash
# Normal transaction
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" \
  -d '{"transaction_id":"tx1","user_id":"user1","amount":50.0,"merchant_name":"Coffee Shop","merchant_category_code":5814,"transaction_type":"purchase","timestamp":"2024-01-01T09:00:00Z"}'

# High amount (potentially fraud)
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" \
  -d '{"transaction_id":"tx2","user_id":"user1","amount":5000.0,"merchant_name":"Online Store","merchant_category_code":5999,"transaction_type":"purchase","timestamp":"2024-01-01T23:00:00Z"}'

# Night transaction (suspicious)
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" \
  -d '{"transaction_id":"tx3","user_id":"user1","amount":500.0,"merchant_name":"Store","merchant_category_code":5411,"transaction_type":"purchase","timestamp":"2024-01-01T03:00:00Z"}'
```

## Stopping the Services

### Stop API Server
Press `Ctrl+C` in the terminal running the API

### Stop Kafka Infrastructure
```bash
docker-compose down
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
- Customize the model by training on your own data
- Deploy to production using Kubernetes

## Troubleshooting

### API won't start
- Check if port 5000 is already in use: `lsof -i :5000`
- Try a different port by modifying `src/api.py`

### Kafka connection errors
- Ensure Docker is running: `docker ps`
- Wait 30-60 seconds after `docker-compose up` for Kafka to be ready
- Check logs: `docker-compose logs kafka`

### Model not loading
- The system will automatically create a default model if files are missing
- Check logs for warnings about model files

### Dependencies installation fails
- Update pip: `pip install --upgrade pip setuptools`
- Try installing packages individually if needed

## Getting Help

- GitHub Issues: [Report a bug](https://github.com/Timmisetty1/Real-Time-Fraud-Detection-Pipeline/issues)
- Documentation: See README.md for more details
- Architecture: See ARCHITECTURE.md for design information
