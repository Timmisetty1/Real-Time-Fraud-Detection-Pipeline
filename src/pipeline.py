"""
Main fraud detection pipeline orchestrator
"""
import logging
import signal
import sys
import time
import yaml
from pathlib import Path

from data_ingestion.kafka_consumer import TransactionConsumer
from data_ingestion.kafka_producer import AlertProducer
from feature_engineering.feature_extractor import FeatureExtractor
from model.fraud_detector import FraudDetector
from scoring.scoring_service import ScoringService
from monitoring.metrics import MetricsCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FraudDetectionPipeline:
    """
    Main pipeline orchestrating all components
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize fraud detection pipeline
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.running = False
        
        # Initialize components
        logger.info("Initializing pipeline components...")
        
        self.metrics = MetricsCollector(
            port=self.config.get('monitoring', {}).get('metrics_port', 8000)
        )
        
        self.feature_extractor = FeatureExtractor(
            self.config.get('features', {})
        )
        
        self.fraud_detector = FraudDetector(
            self.config.get('model', {})
        )
        
        self.alert_producer = AlertProducer(
            self.config.get('kafka', {})
        )
        
        self.scoring_service = ScoringService(
            self.feature_extractor,
            self.fraud_detector,
            self.alert_producer
        )
        
        self.consumer = TransactionConsumer(
            self.config.get('kafka', {})
        )
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Pipeline initialized successfully")
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Return default config
            return {
                'kafka': {
                    'bootstrap_servers': ['localhost:9092'],
                    'consumer_group': 'fraud-detection-consumer',
                    'topics': {'transactions': 'transactions', 'alerts': 'fraud-alerts'}
                },
                'model': {'threshold': 0.7},
                'features': {},
                'monitoring': {'metrics_port': 8000}
            }
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the fraud detection pipeline"""
        logger.info("Starting fraud detection pipeline...")
        
        # Start metrics server
        self.metrics.start()
        
        # Load model
        self.fraud_detector.load_model()
        
        # Connect alert producer
        self.alert_producer.connect()
        
        self.running = True
        self.metrics.set_active_consumers(1)
        
        try:
            # Start consuming transactions
            self.consumer.consume(self._process_transaction)
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
        finally:
            self.stop()
    
    def _process_transaction(self, transaction: dict):
        """
        Process a single transaction
        
        Args:
            transaction: Transaction data from Kafka
        """
        start_time = time.time()
        
        try:
            # Score transaction
            result = self.scoring_service.score_transaction(transaction)
            
            # Record metrics
            processing_time = time.time() - start_time
            self.metrics.record_transaction(
                result.get('is_fraud', False),
                result.get('fraud_probability', 0.0),
                processing_time
            )
            
        except Exception as e:
            logger.error(f"Error processing transaction: {e}", exc_info=True)
            self.metrics.record_error('processing_error')
    
    def stop(self):
        """Stop the pipeline"""
        if not self.running:
            return
        
        logger.info("Stopping pipeline...")
        self.running = False
        
        # Stop consumer
        self.consumer.stop()
        
        # Close connections
        self.alert_producer.close()
        
        # Log statistics
        stats = self.scoring_service.get_statistics()
        logger.info(f"Pipeline statistics: {stats}")
        
        self.metrics.set_active_consumers(0)
        logger.info("Pipeline stopped")
    
    def get_status(self) -> dict:
        """Get pipeline status"""
        return {
            'running': self.running,
            'statistics': self.scoring_service.get_statistics(),
            'model_loaded': self.fraud_detector.model_loaded
        }


def main():
    """Main entry point"""
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config/config.yaml'
    
    pipeline = FraudDetectionPipeline(config_path)
    pipeline.start()


if __name__ == '__main__':
    main()
