"""
Kafka producer for publishing fraud alerts
"""
import json
import logging
from typing import Dict, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class AlertProducer:
    """
    Kafka producer for publishing fraud alerts
    """
    
    def __init__(self, config: Dict):
        """
        Initialize Kafka producer
        
        Args:
            config: Configuration dictionary with Kafka settings
        """
        self.config = config
        self.producer: Optional[KafkaProducer] = None
        
    def connect(self):
        """Establish connection to Kafka broker"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.config['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            logger.info(f"Alert producer connected to Kafka at {self.config['bootstrap_servers']}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to connect producer to Kafka: {e}")
            return False
    
    def send_alert(self, alert: Dict):
        """
        Send fraud alert to Kafka topic
        
        Args:
            alert: Alert dictionary containing fraud detection results
        """
        if not self.producer:
            if not self.connect():
                raise RuntimeError("Failed to connect to Kafka")
        
        try:
            future = self.producer.send(
                self.config['topics']['alerts'],
                value=alert
            )
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Alert sent to topic {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send alert: {e}", exc_info=True)
            return False
    
    def close(self):
        """Close Kafka producer connection"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Alert producer closed")
