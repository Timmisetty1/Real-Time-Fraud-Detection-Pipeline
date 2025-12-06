# System Architecture

## Overview

The Real-Time Fraud Detection Pipeline is a microservices-based system designed to detect fraudulent transactions in real-time with low latency and high throughput.

## Components

### 1. Data Ingestion Layer

#### Kafka Consumer (`src/data_ingestion/kafka_consumer.py`)
- Consumes transaction events from Kafka topics
- Deserializes JSON messages
- Handles connection failures and retries
- Supports consumer groups for horizontal scaling

#### Kafka Producer (`src/data_ingestion/kafka_producer.py`)
- Publishes fraud alerts to Kafka topics
- Ensures message delivery with acknowledgments
- Handles backpressure and retries

### 2. Feature Engineering Layer

#### Feature Extractor (`src/feature_engineering/feature_extractor.py`)
- Extracts 15+ features from raw transaction data
- Maintains in-memory state for velocity calculations
- Computes user behavioral patterns
- Generates temporal features

**Features Generated:**
- **Basic**: amount, merchant_category_code, transaction_type
- **Temporal**: hour, day, is_weekend, is_night
- **User Behavioral**: total_transactions, avg_amount, std_amount
- **Velocity**: transactions and amount in last 1h and 24h
- **Derived**: z-scores for anomaly detection

### 3. Model Layer

#### Fraud Detector (`src/model/fraud_detector.py`)
- Random Forest or XGBoost classifier
- Standardizes features using scikit-learn's StandardScaler
- Configurable fraud probability threshold
- Supports model serialization/deserialization

**Model Architecture:**
```
Input Features (15 dimensions)
    ↓
StandardScaler (normalization)
    ↓
Random Forest / XGBoost
    ↓
Binary Classification (fraud/legitimate)
    ↓
Probability Score (0.0 - 1.0)
```

### 4. Scoring Service

#### Scoring Service (`src/scoring/scoring_service.py`)
- Orchestrates feature extraction and prediction
- Tracks statistics (processed, fraud count, etc.)
- Triggers alerts for high-risk transactions
- Measures processing latency

### 5. Monitoring Layer

#### Metrics Collector (`src/monitoring/metrics.py`)
- Exposes Prometheus metrics on port 8000
- Tracks key performance indicators:
  - Throughput (transactions/second)
  - Latency (processing time)
  - Fraud rate
  - Error rate
- Histogram-based distributions

### 6. API Layer

#### REST API (`src/api.py`)
- Flask-based web service
- Endpoints:
  - `POST /predict` - Single transaction scoring
  - `POST /batch_predict` - Batch scoring
  - `GET /health` - Health check
  - `GET /statistics` - Runtime statistics
  - `GET /feature_importance` - Model insights

## Data Flow

### Streaming Mode

```
Transaction Source
    ↓
Kafka Topic (transactions)
    ↓
Kafka Consumer
    ↓
Feature Extractor
    ↓
Fraud Detector
    ↓
Scoring Service
    ↓ (if fraud)
Alert Producer
    ↓
Kafka Topic (fraud-alerts)
```

### API Mode

```
HTTP Request
    ↓
Flask API
    ↓
Feature Extractor
    ↓
Fraud Detector
    ↓
HTTP Response (JSON)
```

## System Design Decisions

### 1. In-Memory State Management

**Decision**: Use Python dictionaries for velocity calculations
**Rationale**: 
- Low latency (microseconds)
- Simple implementation
- Sufficient for demo/MVP

**Production Alternative**: Redis/Memcached for distributed state

### 2. Feature Engineering

**Decision**: Real-time feature computation
**Rationale**:
- Freshest data for predictions
- No dependency on external feature store
- Full control over feature logic

**Trade-offs**:
- Higher CPU usage
- State management complexity

### 3. Model Selection

**Decision**: Random Forest as default
**Rationale**:
- Fast inference (<1ms)
- No need for GPU
- Interpretable feature importance
- Robust to feature scaling issues

**Alternative**: XGBoost for better accuracy (configurable)

### 4. Asynchronous Processing

**Decision**: Synchronous processing in consumer callback
**Rationale**:
- Simpler error handling
- Back-pressure from Kafka
- Easier debugging

**Production Alternative**: Async I/O with asyncio for higher throughput

## Scalability

### Horizontal Scaling

1. **Kafka Partitions**: Increase topic partitions
2. **Consumer Instances**: Deploy multiple consumer instances
3. **Consumer Groups**: Automatic load balancing
4. **API Instances**: Run multiple API servers behind load balancer

### Vertical Scaling

1. **CPU**: Feature engineering is CPU-bound
2. **Memory**: State management (velocity features)
3. **Network**: Kafka throughput

### Performance Characteristics

- **Throughput**: 1000+ TPS per instance
- **Latency**: <10ms p99
- **Memory**: ~500MB base + state
- **CPU**: ~50% utilization at 1000 TPS

## Fault Tolerance

### Kafka Consumer
- Auto-reconnect on broker failure
- Consumer group rebalancing
- Offset management for at-least-once delivery

### Model Loading
- Fallback to synthetic model if file not found
- Graceful degradation

### Error Handling
- Try-catch blocks in critical paths
- Logging for all errors
- Metrics for error tracking

## Security Considerations

### Current State (MVP)
- No authentication
- No encryption
- No input validation beyond basic checks

### Production Requirements
1. **Authentication**: API keys, OAuth 2.0
2. **Encryption**: TLS for all network traffic
3. **Input Validation**: Strict schema validation
4. **Rate Limiting**: Prevent abuse
5. **Audit Logging**: Track all predictions
6. **PII Handling**: Anonymize sensitive data

## Future Enhancements

### Short Term
1. Redis integration for distributed state
2. Model versioning and A/B testing
3. Enhanced monitoring dashboards
4. Circuit breakers for external dependencies

### Long Term
1. Graph-based fraud detection
2. Deep learning models (LSTM, Transformers)
3. Real-time model retraining
4. Multi-model ensemble
5. Explainable AI (SHAP, LIME)
6. Feedback loop for model improvement

## Technology Stack

- **Language**: Python 3.8+
- **ML Framework**: scikit-learn, XGBoost
- **Streaming**: Apache Kafka
- **API**: Flask
- **Monitoring**: Prometheus
- **Containerization**: Docker
- **Orchestration**: Docker Compose (Kubernetes-ready)

## Deployment Topologies

### Development
```
Single Machine
├── Kafka (Docker)
├── Zookeeper (Docker)
├── Pipeline (Local Python)
└── API (Local Python)
```

### Production
```
Kubernetes Cluster
├── Kafka StatefulSet (3 replicas)
├── Pipeline Deployment (N replicas)
├── API Deployment (M replicas)
├── Prometheus (monitoring)
└── Grafana (dashboards)
```

## Configuration Management

- **Config Files**: YAML for readability
- **Environment Variables**: Override config
- **Secrets**: External secret management (Vault, AWS Secrets Manager)

## Testing Strategy

### Unit Tests
- Feature extraction logic
- Model predictions
- Scoring service

### Integration Tests
- Kafka connectivity
- End-to-end pipeline
- API endpoints

### Performance Tests
- Load testing (locust, k6)
- Latency benchmarks
- Memory profiling

## Monitoring & Observability

### Metrics
- Business: fraud_rate, false_positive_rate
- Technical: throughput, latency, error_rate
- System: CPU, memory, network

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized logging (ELK stack)

### Alerting
- High error rate
- Latency spikes
- Kafka lag
- Model drift

## Cost Optimization

1. **Right-sizing**: Monitor resource usage
2. **Auto-scaling**: Scale based on load
3. **Spot Instances**: For non-critical workloads
4. **Data Retention**: Archive old Kafka messages
5. **Model Optimization**: Quantization, pruning
