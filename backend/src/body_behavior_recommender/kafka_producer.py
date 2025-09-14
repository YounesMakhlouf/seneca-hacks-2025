"""Kafka producer for sending feedback messages to async worker."""

import json
import os
from typing import Dict, Any
from datetime import datetime
import logging

from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class FeedbackKafkaProducer:
    """Kafka producer for sending feedback messages to async processing."""
    
    def __init__(self):
        self.producer = None
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = os.getenv('KAFKA_TOPIC', 'feedback')
        
    def initialize(self):
        """Initialize Kafka producer connection."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                retry_backoff_ms=1000,
            )
            logger.info(f"Kafka producer initialized. Servers: {self.bootstrap_servers}, Topic: {self.topic}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise
    
    def send_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Send feedback message to Kafka topic.
        
        Args:
            feedback_data: Dictionary containing feedback information
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
            
        try:
            # Create message with metadata
            message = {
                "id": f"feedback_{int(datetime.now().timestamp()*1000)}",
                "timestamp": datetime.now().timestamp(),
                "feedback": feedback_data
            }
            
            # Send message using user_id as key for partitioning
            future = self.producer.send(
                self.topic,
                value=message,
                key=feedback_data.get('user_id')
            )
            
            # Wait for send to complete (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Feedback message sent to topic {record_metadata.topic} "
                       f"partition {record_metadata.partition} "
                       f"offset {record_metadata.offset}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send feedback message to Kafka: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending feedback message: {e}")
            return False
    
    def close(self):
        """Close Kafka producer connection."""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")


# Global producer instance
_kafka_producer = None


def get_kafka_producer() -> FeedbackKafkaProducer:
    """Get global Kafka producer instance."""
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = FeedbackKafkaProducer()
        _kafka_producer.initialize()
    return _kafka_producer


def send_feedback_async(feedback_data: Dict[str, Any]) -> bool:
    """Send feedback message for async processing.
    
    Args:
        feedback_data: Dictionary containing feedback information
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    producer = get_kafka_producer()
    return producer.send_feedback(feedback_data)