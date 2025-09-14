"""MongoDB integration layer."""

import os
from typing import Any, Dict, List, Optional

from .models import (
    ActivityEntry,
    MeasurementEntry,
    NutritionEntry,
    SleepEntry,
    UserProfile,
)
from .mongo_wrapper import MongoClientWrapper

MONGO_DB_NAME = os.getenv("BBR_DB_NAME", "bbr")
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://bbr:bbrpass@mongo:27017/?authSource=admin&directConnection=true",
)

COLLECTIONS = {
    "users": "users",
    "sleep": "sleep",
    "nutrition": "nutrition",
    "activity": "activity",
    "measurements": "measurements",
}

COLLECTION_MODELS = {
    "users": UserProfile,
    "sleep": SleepEntry,
    "nutrition": NutritionEntry,
    "activity": ActivityEntry,
    "measurements": MeasurementEntry,
}


# ---------- Access Helpers ----------
def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by ID from MongoDB."""
    with MongoClientWrapper(
        UserProfile, COLLECTIONS["users"], MONGO_DB_NAME, MONGODB_URI
    ) as client:
        users = client.fetch_documents(1, {"user_id": user_id})
        return users[0].model_dump() if users else None


def get_users(limit: int = 50) -> List[Dict[str, Any]]:
    """Get multiple users from MongoDB."""
    with MongoClientWrapper(
        UserProfile, COLLECTIONS["users"], MONGO_DB_NAME, MONGODB_URI
    ) as client:
        users = client.fetch_documents(limit, {})
        return [u.model_dump() for u in users]


def get_recent_entries(
    collection: str, user_id: str, limit: int = 7
) -> List[Dict[str, Any]]:
    """Get recent entries for a user from MongoDB."""
    model = COLLECTION_MODELS.get(collection)
    if not model:
        return []

    with MongoClientWrapper(
        model, COLLECTIONS[collection], MONGO_DB_NAME, MONGODB_URI
    ) as client:
        # Get recent entries sorted by date (descending first, then reverse for chronological asc)
        docs = client.fetch_documents(
            limit * 2, {"user_id": user_id}
        )  # Fetch more to sort properly
        docs = sorted(docs, key=lambda d: getattr(d, "date", ""), reverse=True)[:limit]
        return [d.model_dump() for d in reversed(docs)]


def get_user_measurements(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent measurements for a user from MongoDB."""
    with MongoClientWrapper(
        MeasurementEntry, COLLECTIONS["measurements"], MONGO_DB_NAME, MONGODB_URI
    ) as client:
        docs = client.fetch_documents(limit * 2, {"user_id": user_id})
        docs = sorted(docs, key=lambda d: getattr(d, "date", ""), reverse=True)[:limit]
        return [d.model_dump() for d in docs]


def insert_many(collection: str, docs: List[Dict[str, Any]]):
    """Insert many documents into a MongoDB collection."""
    if not docs:
        return

    model = COLLECTION_MODELS.get(collection)
    if not model:
        return

    with MongoClientWrapper(
        model, COLLECTIONS[collection], MONGO_DB_NAME, MONGODB_URI
    ) as client:
        try:
            # Convert dicts to Pydantic models
            instances = [model.model_validate(doc) for doc in docs]
            client.ingest_documents(instances)
        except Exception:
            pass  # ignore duplicates etc. during seeding


def collection_count(collection: str) -> int:
    """Get count of documents in a MongoDB collection."""
    model = COLLECTION_MODELS.get(collection)
    if not model:
        return 0

    with MongoClientWrapper(
        model, COLLECTIONS[collection], MONGO_DB_NAME, MONGODB_URI
    ) as client:
        return client.get_collection_count()
