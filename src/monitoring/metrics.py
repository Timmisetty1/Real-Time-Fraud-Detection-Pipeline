"""
Prometheus metrics for monitoring fraud detection pipeline
"""
import logging
from prometheus_client import Counter, Histogram, Gauge, start_http_server

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collect and expose metrics for monitoring
    """
    
    def __init__(self, port: int = 8000):
        """
        Initialize metrics collector
        
        Args:
            port: Port to expose metrics on
        """
        self.port = port
        
        # Define metrics
        self.transactions_processed = Counter(
            'fraud_detection_transactions_processed_total',
            'Total number of transactions processed'
        )
        
        self.fraud_detected = Counter(
            'fraud_detection_fraud_detected_total',
            'Total number of fraudulent transactions detected'
        )
        
        self.processing_time = Histogram(
            'fraud_detection_processing_seconds',
            'Time spent processing transactions',
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )
        
        self.fraud_probability = Histogram(
            'fraud_detection_probability',
            'Distribution of fraud probability scores',
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        self.active_consumers = Gauge(
            'fraud_detection_active_consumers',
            'Number of active Kafka consumers'
        )
        
        self.errors = Counter(
            'fraud_detection_errors_total',
            'Total number of errors',
            ['error_type']
        )
        
        self.model_predictions = Counter(
            'fraud_detection_predictions_total',
            'Total predictions by class',
            ['prediction']
        )
    
    def start(self):
        """Start metrics HTTP server"""
        try:
            start_http_server(self.port)
            logger.info(f"Metrics server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    def record_transaction(self, is_fraud: bool, probability: float, processing_time: float):
        """
        Record transaction metrics
        
        Args:
            is_fraud: Whether transaction was classified as fraud
            probability: Fraud probability score
            processing_time: Time taken to process transaction
        """
        self.transactions_processed.inc()
        self.processing_time.observe(processing_time)
        self.fraud_probability.observe(probability)
        
        if is_fraud:
            self.fraud_detected.inc()
            self.model_predictions.labels(prediction='fraud').inc()
        else:
            self.model_predictions.labels(prediction='legitimate').inc()
    
    def record_error(self, error_type: str):
        """
        Record error
        
        Args:
            error_type: Type of error that occurred
        """
        self.errors.labels(error_type=error_type).inc()
    
    def set_active_consumers(self, count: int):
        """
        Set number of active consumers
        
        Args:
            count: Number of active consumers
        """
        self.active_consumers.set(count)
