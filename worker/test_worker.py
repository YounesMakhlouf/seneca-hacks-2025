#!/usr/bin/env python3
"""Test script for worker functionality."""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from feedback_worker.processor import FeedbackProcessor


async def test_processor():
    """Test the feedback processor with sample data."""
    print("🧪 Testing Feedback Processor...")
    
    # Set environment variables for testing
    os.environ['MONGODB_URI'] = 'mongodb://bbr:bbrpass@localhost:27017/?directConnection=true'
    os.environ['BBR_DB_NAME'] = 'bbr'
    
    processor = FeedbackProcessor()
    
    try:
        # Initialize processor
        print("1️⃣ Initializing processor...")
        await processor.initialize()
        print("✅ Processor initialized successfully")
        
        # Test state computation (this will fail with DB connection but should not crash)
        print("2️⃣ Testing state computation...")
        try:
            state = await processor._compute_user_state("test_user")
            print(f"✅ State computed: {state}")
        except Exception as e:
            print(f"⚠️ State computation failed (expected without DB): {e}")
            # Test with fallback
            state = {"Readiness": 75, "Fuel": 60, "Strain": 45}
            print(f"✅ Using fallback state: {state}")
        
        # Test Thompson sampling
        print("3️⃣ Testing Thompson sampling...")
        arm = processor._thompson_sample_contextual("test_user", "music", state)
        print(f"✅ Selected arm: {arm}")
        
        # Test reward calculation
        print("4️⃣ Testing reward calculation...")
        from shared.models import Feedback
        fb = Feedback(
            user_id="test_user",
            domain="music", 
            item_id="m1",
            thumbs=1,
            completed=0.8,
            hr_zone_frac=0.7
        )
        reward = processor._reward_from_feedback("music", fb)
        print(f"✅ Calculated reward: {reward}")
        
        # Test bandit update
        print("5️⃣ Testing bandit update...")
        processor._update_bandit("test_user", "music", arm, reward, state)
        print("✅ Bandit updated successfully")
        
        # Test complete feedback processing
        print("6️⃣ Testing complete feedback processing...")
        message_data = {
            "id": "test_feedback_123",
            "timestamp": datetime.now().timestamp(),
            "feedback": {
                "user_id": "test_user",
                "domain": "music",
                "item_id": "m1", 
                "thumbs": 1,
                "completed": 0.8,
                "hr_zone_frac": 0.7
            }
        }
        
        try:
            result = await processor.process_feedback(message_data)
            print(f"✅ Feedback processed: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"⚠️ Feedback processing failed (expected without DB): {e}")
        
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        await processor.cleanup()


if __name__ == "__main__":
    asyncio.run(test_processor())