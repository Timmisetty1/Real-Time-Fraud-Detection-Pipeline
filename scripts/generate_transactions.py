"""
Transaction data generator for testing the fraud detection pipeline
"""
import json
import random
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransactionGenerator:
    """Generate synthetic transaction data"""
    
    def __init__(self, bootstrap_servers=['localhost:9092']):
        """Initialize transaction generator"""
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        
        self.merchants = [
            'Amazon', 'Walmart', 'Target', 'Best Buy', 'Apple Store',
            'Gas Station', 'Restaurant', 'Coffee Shop', 'Grocery Store',
            'Online Retailer', 'Department Store', 'Electronics Store'
        ]
        
        self.transaction_types = ['purchase', 'withdrawal', 'transfer', 'payment']
        
        self.merchant_categories = {
            'Amazon': 5999,
            'Walmart': 5411,
            'Target': 5411,
            'Best Buy': 5732,
            'Apple Store': 5732,
            'Gas Station': 5541,
            'Restaurant': 5812,
            'Coffee Shop': 5814,
            'Grocery Store': 5411,
            'Online Retailer': 5999,
            'Department Store': 5311,
            'Electronics Store': 5732
        }
    
    def connect(self):
        """Connect to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
    
    def generate_transaction(self, user_id=None, is_fraud=False):
        """Generate a single transaction"""
        if not user_id:
            user_id = f"user_{random.randint(1000, 9999)}"
        
        merchant = random.choice(self.merchants)
        transaction_type = random.choice(self.transaction_types)
        
        # Normal transaction amounts
        if not is_fraud:
            if merchant in ['Coffee Shop', 'Restaurant']:
                amount = round(random.uniform(5, 50), 2)
            elif merchant in ['Gas Station']:
                amount = round(random.uniform(20, 80), 2)
            elif merchant in ['Grocery Store']:
                amount = round(random.uniform(30, 200), 2)
            else:
                amount = round(random.uniform(50, 500), 2)
        else:
            # Fraudulent transactions - unusually high amounts
            amount = round(random.uniform(1000, 5000), 2)
        
        transaction = {
            'transaction_id': f"tx_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            'user_id': user_id,
            'amount': amount,
            'merchant_name': merchant,
            'merchant_category_code': self.merchant_categories[merchant],
            'transaction_type': transaction_type,
            'timestamp': datetime.now().isoformat()
        }
        
        return transaction
    
    def send_transaction(self, transaction, topic='transactions'):
        """Send transaction to Kafka topic"""
        if not self.producer:
            if not self.connect():
                raise RuntimeError("Cannot send transaction: not connected to Kafka")
        
        try:
            future = self.producer.send(topic, value=transaction)
            future.get(timeout=10)
            logger.info(f"Sent transaction: {transaction['transaction_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to send transaction: {e}")
            return False
    
    def generate_stream(self, num_transactions=100, fraud_rate=0.1, delay=1.0):
        """
        Generate a stream of transactions
        
        Args:
            num_transactions: Number of transactions to generate
            fraud_rate: Proportion of fraudulent transactions
            delay: Delay between transactions in seconds
        """
        logger.info(f"Generating {num_transactions} transactions with {fraud_rate*100}% fraud rate")
        
        users = [f"user_{random.randint(1000, 1999)}" for _ in range(20)]
        
        for i in range(num_transactions):
            user_id = random.choice(users)
            is_fraud = random.random() < fraud_rate
            
            transaction = self.generate_transaction(user_id, is_fraud)
            
            try:
                self.send_transaction(transaction)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Progress: {i + 1}/{num_transactions} transactions sent")
                
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error sending transaction {i}: {e}")
        
        logger.info("Stream generation complete")
    
    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Producer closed")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate synthetic transactions')
    parser.add_argument('--num', type=int, default=100, help='Number of transactions')
    parser.add_argument('--fraud-rate', type=float, default=0.1, help='Fraud rate (0-1)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between transactions')
    parser.add_argument('--kafka', default='localhost:9092', help='Kafka bootstrap servers')
    
    args = parser.parse_args()
    
    generator = TransactionGenerator([args.kafka])
    
    try:
        generator.generate_stream(
            num_transactions=args.num,
            fraud_rate=args.fraud_rate,
            delay=args.delay
        )
    except KeyboardInterrupt:
        logger.info("Generation interrupted by user")
    finally:
        generator.close()


if __name__ == '__main__':
    main()
