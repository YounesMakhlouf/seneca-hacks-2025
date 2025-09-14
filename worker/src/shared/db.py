"""MongoDB database helper functions for worker."""

import os
from typing import List, Dict, Any, Optional
from .models import UserProfile, SleepEntry, NutritionEntry, ActivityEntry, MeasurementEntry


def get_user(client, db_name: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by ID from MongoDB."""
    try:
        db = client[db_name]
        collection = db['users']
        user_doc = collection.find_one({"user_id": user_id})
        return user_doc
    except Exception as e:
        raise RuntimeError(f"Error getting user {user_id}: {e}")


def get_recent_entries(client, db_name: str, collection_name: str, user_id: str, limit: int = 7) -> List[Dict[str,Any]]:
    """Get recent entries for a user from MongoDB."""
    try:
        db = client[db_name]
        collection = db[collection_name]
        
        # Get recent entries sorted by date descending, then reverse for chronological order
        cursor = collection.find({"user_id": user_id}).sort("date", -1).limit(limit * 2)
        docs = list(cursor)
        
        # Sort by date and take most recent entries
        docs = sorted(docs, key=lambda d: d.get("date", ""), reverse=True)[:limit]
        return list(reversed(docs))  # Return in chronological order
        
    except Exception as e:
        raise RuntimeError(f"Error getting recent entries for {user_id} from {collection_name}: {e}")