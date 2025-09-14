"""Kafka consumer and feedback processor."""

import json
import logging
import os
import time
from typing import Dict, Any, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import asyncio

logger = logging.getLogger(__name__)


class FeedbackWorker:
    """Async feedback processor that consumes from Kafka and processes feedback."""
    
    def __init__(self):
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        self.topic = os.getenv('KAFKA_TOPIC', 'feedback')
        self.group_id = os.getenv('KAFKA_GROUP_ID', 'feedback-worker')
        self.poll_timeout = float(os.getenv('WORKER_POLL_TIMEOUT', '1.0'))
        self.max_poll_records = int(os.getenv('WORKER_MAX_POLL_RECORDS', '10'))
        self.retry_attempts = int(os.getenv('WORKER_RETRY_ATTEMPTS', '3'))
        self.retry_delay = float(os.getenv('WORKER_RETRY_DELAY', '5.0'))
        
        self.consumer = None
        self.processor = None
        self.running = False
        
        logger.info(f"🔧 Worker configured: {self.kafka_servers}/{self.topic}")
    
    def _create_consumer(self) -> KafkaConsumer:
        """Create and configure Kafka consumer."""
        try:
            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.kafka_servers],
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                consumer_timeout_ms=int(self.poll_timeout * 1000),
                max_poll_records=self.max_poll_records
            )
            logger.info(f"✅ Kafka consumer created for topic: {self.topic}")
            return consumer
        except Exception as e:
            logger.error(f"❌ Failed to create Kafka consumer: {e}")
            raise
    
    async def run(self):
        """Main worker loop."""
        logger.info("🚀 Starting feedback worker...")
        
        # Initialize processor
        from .processor import FeedbackProcessor
        self.processor = FeedbackProcessor()
        await self.processor.initialize()
        
        # Create consumer
        self.consumer = self._create_consumer()
        self.running = True
        
        try:
            while self.running:
                await self._poll_and_process()
                
        except KeyboardInterrupt:
            logger.info("📝 Worker stopped by user")
        except Exception as e:
            logger.error(f"❌ Worker error: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _poll_and_process(self):
        """Poll for messages and process them."""
        try:
            # Poll for messages (blocking with timeout)
            message_batch = self.consumer.poll(timeout_ms=int(self.poll_timeout * 1000))
            
            if not message_batch:
                # No messages, short sleep to prevent busy waiting
                await asyncio.sleep(0.1)
                return
            
            # Process messages
            for topic_partition, messages in message_batch.items():
                for message in messages:
                    await self._process_message(message.value)
                    
        except KafkaError as e:
            logger.error(f"❌ Kafka error: {e}")
            await asyncio.sleep(self.retry_delay)
        except Exception as e:
            logger.error(f"❌ Processing error: {e}")
            await asyncio.sleep(1.0)
    
    async def _process_message(self, message_data: Dict[str, Any]):
        """Process a single feedback message with retry logic."""
        feedback_id = message_data.get('id', 'unknown')
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"📝 Processing feedback {feedback_id} (attempt {attempt + 1})")
                
                # Process the feedback
                result = await self.processor.process_feedback(message_data)
                
                logger.info(f"✅ Feedback {feedback_id} processed successfully: {result}")
                return
                
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed for {feedback_id}: {e}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"💀 Feedback {feedback_id} failed after {self.retry_attempts} attempts")
                    # In production, you might want to send to a dead letter queue
    
    async def _cleanup(self):
        """Clean up resources."""
        self.running = False
        
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("📝 Kafka consumer closed")
            except Exception as e:
                logger.error(f"❌ Error closing consumer: {e}")
        
        if self.processor:
            try:
                await self.processor.cleanup()
                logger.info("📝 Processor cleaned up")
            except Exception as e:
                logger.error(f"❌ Error cleaning up processor: {e}")
    
    def stop(self):
        """Signal the worker to stop."""
        logger.info("🛑 Stop signal received")
        self.running = False