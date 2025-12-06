# Real-Time Fraud Detection Pipeline

A scalable, production-ready fraud detection system that processes transactions in real-time using machine learning and stream processing.

## Features

- **Real-time Processing**: Kafka-based stream processing for high-throughput transaction analysis
- **Machine Learning**: XGBoost/Random Forest models for fraud detection
- **Feature Engineering**: Automated extraction of 15+ features including velocity and behavioral patterns
- **REST API**: Flask-based API for synchronous predictions
- **Monitoring**: Prometheus metrics for system observability
- **Alerting**: Automatic fraud alerts published to Kafka
- **Scalable**: Containerized architecture with Docker support

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Transaction │────▶│    Kafka     │────▶│ Fraud Detection │
│   Source    │     │   (Stream)   │     │    Pipeline     │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                           ┌───────────────────────┼────────────────┐
                           ▼                       ▼                ▼
                    ┌─────────────┐        ┌────────────┐   ┌──────────┐
                    │   Feature   │───────▶│ ML Model   │──▶│  Alert   │
                    │ Engineering │        │  (XGBoost) │   │ Producer │
                    └─────────────┘        └────────────┘   └────┬─────┘
                                                                  │
                                                                  ▼
                                                           ┌──────────────┐
                                                           │ Fraud Alerts │
                                                           │    Topic     │
                                                           └──────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Timmisetty1/Real-Time-Fraud-Detection-Pipeline.git
cd Real-Time-Fraud-Detection-Pipeline
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start Kafka infrastructure:
```bash
docker-compose up -d
```

Wait for Kafka to be ready (about 30 seconds).

### Running the Pipeline

#### Option 1: Stream Processing Mode

Start the fraud detection pipeline to consume from Kafka:

```bash
cd src
python pipeline.py
```

In another terminal, generate test transactions:

```bash
python scripts/generate_transactions.py --num 50 --fraud-rate 0.2 --delay 0.5
```

#### Option 2: REST API Mode

Start the API server:

```bash
cd src
python api.py
```

The API will be available at `http://localhost:5000`.

Test with curl:

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx123",
    "user_id": "user456",
    "amount": 1500.00,
    "merchant_name": "Amazon",
    "merchant_category_code": 5999,
    "transaction_type": "purchase",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

## API Endpoints

### POST /predict
Predict fraud for a single transaction.

**Request:**
```json
{
  "transaction_id": "tx123",
  "user_id": "user456",
  "amount": 150.50,
  "merchant_name": "Amazon",
  "merchant_category_code": 5411,
  "transaction_type": "purchase",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response:**
```json
{
  "transaction_id": "tx123",
  "user_id": "user456",
  "amount": 150.50,
  "is_fraud": false,
  "fraud_probability": 0.1234,
  "scoring_timestamp": "2024-01-01T12:00:01Z"
}
```

### POST /batch_predict
Predict fraud for multiple transactions.

### GET /health
Health check endpoint.

### GET /statistics
Get pipeline statistics.

### GET /feature_importance
Get model feature importance scores.

### POST /reset_statistics
Reset statistics counters.

## Features Extracted

The pipeline extracts and engineers 15+ features:

### Basic Features
- `amount`: Transaction amount
- `merchant_category_code`: Merchant category
- `transaction_type`: Type of transaction

### Temporal Features
- `transaction_hour`: Hour of day (0-23)
- `transaction_day`: Day of week (0-6)
- `is_weekend`: Weekend flag
- `is_night`: Night time flag (10 PM - 6 AM)

### User Behavioral Features
- `user_total_transactions`: Total transactions by user
- `user_avg_amount`: User's average transaction amount
- `user_std_amount`: Standard deviation of user's transactions

### Velocity Features
- `velocity_1h`: Number of transactions in last hour
- `velocity_24h`: Number of transactions in last 24 hours
- `amount_1h`: Total amount spent in last hour
- `amount_24h`: Total amount spent in last 24 hours

### Derived Features
- `amount_z_score`: Z-score of amount based on user's history

## Configuration

Edit `config/config.yaml` to customize:

```yaml
kafka:
  bootstrap_servers: ["localhost:9092"]
  consumer_group: "fraud-detection-consumer"
  topics:
    transactions: "transactions"
    alerts: "fraud-alerts"

model:
  path: "models/fraud_detection_model.pkl"
  threshold: 0.7

monitoring:
  metrics_port: 8000
```

## Monitoring

Prometheus metrics are exposed on port 8000:

- `fraud_detection_transactions_processed_total`: Total transactions processed
- `fraud_detection_fraud_detected_total`: Total fraud detected
- `fraud_detection_processing_seconds`: Processing time histogram
- `fraud_detection_probability`: Fraud probability distribution
- `fraud_detection_errors_total`: Total errors

View metrics: `http://localhost:8000`

Access Kafka UI: `http://localhost:8080`

## Development

### Project Structure

```
.
├── config/
│   └── config.yaml          # Configuration file
├── src/
│   ├── data_ingestion/      # Kafka consumer/producer
│   ├── feature_engineering/ # Feature extraction
│   ├── model/               # ML model
│   ├── scoring/             # Scoring service
│   ├── monitoring/          # Metrics collection
│   ├── pipeline.py          # Main pipeline
│   └── api.py               # REST API
├── scripts/
│   └── generate_transactions.py  # Test data generator
├── tests/                   # Unit tests
├── data/                    # Data files
├── docker-compose.yml       # Docker setup
└── requirements.txt         # Python dependencies
```

### Running Tests

```bash
pytest tests/
```

### Training a Custom Model

To train your own model, prepare a dataset with labeled transactions and use scikit-learn or XGBoost:

```python
from src.model.fraud_detector import FraudDetector
import pandas as pd

# Load your data
df = pd.read_csv('your_data.csv')
X = df[feature_columns]
y = df['is_fraud']

# Train model
detector = FraudDetector(config)
detector.model.fit(X, y)
detector.save_model()
```

## Deployment

### Docker Deployment

Build and run the entire stack:

```bash
docker-compose up -d
```

### Production Considerations

1. **Kafka**: Use a managed Kafka service (AWS MSK, Confluent Cloud)
2. **Model Storage**: Store models in S3/Azure Blob
3. **State Management**: Use Redis for velocity features
4. **Monitoring**: Integrate with Prometheus/Grafana
5. **Scaling**: Run multiple consumer instances
6. **Security**: Add authentication and encryption

## Performance

- **Throughput**: 1000+ transactions/second per instance
- **Latency**: < 10ms average processing time
- **Scalability**: Horizontally scalable with Kafka partitions

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/Timmisetty1/Real-Time-Fraud-Detection-Pipeline/issues)
- Documentation: See this README

## Roadmap

- [ ] Deep learning models (LSTM, Transformer)
- [ ] Graph-based fraud detection
- [ ] Real-time model retraining
- [ ] Advanced feature store integration
- [ ] Multi-model ensemble
- [ ] Explainable AI features