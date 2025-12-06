"""
Kafka consumer for ingesting real-time transaction data
"""
import json
import logging
from typing import Dict, Callable, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class TransactionConsumer:
    """
    Kafka consumer for processing transaction streams in real-time
    """
    
    def __init__(self, config: Dict):
        """
        Initialize Kafka consumer
        
        Args:
            config: Configuration dictionary with Kafka settings
        """
        self.config = config
        self.consumer: Optional[KafkaConsumer] = None
        self.running = False
        
    def connect(self):
        """Establish connection to Kafka broker"""
        try:
            self.consumer = KafkaConsumer(
                self.config['topics']['transactions'],
                bootstrap_servers=self.config['bootstrap_servers'],
                group_id=self.config['consumer_group'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                max_poll_records=100
            )
            logger.info(f"Connected to Kafka broker at {self.config['bootstrap_servers']}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
    
    def consume(self, callback: Callable[[Dict], None]):
        """
        Start consuming messages and process them with callback
        
        Args:
            callback: Function to process each transaction
        """
        if not self.consumer:
            if not self.connect():
                raise RuntimeError("Failed to connect to Kafka")
        
        self.running = True
        logger.info("Started consuming transactions...")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                    
                transaction = message.value
                logger.debug(f"Received transaction: {transaction.get('transaction_id', 'unknown')}")
                
                try:
                    callback(transaction)
                except Exception as e:
                    logger.error(f"Error processing transaction: {e}", exc_info=True)
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
        finally:
            self.close()
    
    def stop(self):
        """Stop consuming messages"""
        self.running = False
        logger.info("Stopping consumer...")
    
    def close(self):
        """Close Kafka consumer connection"""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")
