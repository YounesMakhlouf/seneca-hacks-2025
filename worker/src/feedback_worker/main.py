"""Main entry point for the feedback worker."""

from .worker import FeedbackWorker
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the feedback worker."""
    logger.info("🚀 Starting Feedback Worker...")
    
    worker = FeedbackWorker()
    
    try:
        # Run the worker
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        logger.info("📝 Feedback Worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Feedback Worker failed: {e}")
        raise

if __name__ == "__main__":
    main()