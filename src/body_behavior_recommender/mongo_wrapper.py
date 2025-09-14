"""
Generic MongoDB wrapper for Pydantic models.

Provides type-safe ingestion, querying, and validation for any Pydantic model.
Usage:
    from models import UserProfile
    wrapper = MongoClientWrapper(UserProfile, "users")
    wrapper.ingest_documents([...])
    users = wrapper.fetch_documents(10, {})
    ...
"""
from typing import Generic, Type, TypeVar, List, Dict, Any
from bson import ObjectId
from pydantic import BaseModel
from pymongo import MongoClient, errors
import os

T = TypeVar("T", bound=BaseModel)

class MongoClientWrapper(Generic[T]):
    def __init__(
        self,
        model: Type[T],
        collection_name: str,
        database_name: str = None,
        mongodb_uri: str = None,
    ) -> None:
        self.model = model
        self.collection_name = collection_name
        self.database_name = database_name or os.getenv("BBR_DB_NAME", "bbr")
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_URI", "mongodb://bbr:bbrpass@localhost:27017/?authSource=admin")
        try:
            self.client = MongoClient(self.mongodb_uri, appname="body_behavior_recommender")
            self.client.admin.command("ping")
        except Exception as e:
            print(f"Failed to initialize MongoClientWrapper: {e}")
            raise
        self.database = self.client[self.database_name]
        self.collection = self.database[self.collection_name]
        print(f"Connected to MongoDB: {self.mongodb_uri} DB: {self.database_name} Collection: {self.collection_name}")

    def __enter__(self) -> "MongoClientWrapper":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def clear_collection(self) -> None:
        try:
            result = self.collection.delete_many({})
            print(f"Cleared collection. Deleted {result.deleted_count} documents.")
        except errors.PyMongoError as e:
            print(f"Error clearing the collection: {e}")
            raise

    def ingest_documents(self, documents: List[T]) -> None:
        try:
            if not documents or not all(isinstance(doc, BaseModel) for doc in documents):
                raise ValueError("Documents must be a list of Pydantic models.")
            dict_documents = [doc.model_dump() for doc in documents]
            for doc in dict_documents:
                doc.pop("_id", None)
            self.collection.insert_many(dict_documents)
            print(f"Inserted {len(documents)} documents into MongoDB.")
        except errors.PyMongoError as e:
            print(f"Error inserting documents: {e}")
            raise

    def fetch_documents(self, limit: int, query: Dict[str, Any]) -> List[T]:
        try:
            documents = list(self.collection.find(query).limit(limit))
            print(f"Fetched {len(documents)} documents with query: {query}")
            return self.__parse_documents(documents)
        except Exception as e:
            print(f"Error fetching documents: {e}")
            raise

    def __parse_documents(self, documents: List[Dict[str, Any]]) -> List[T]:
        parsed_documents = []
        for doc in documents:
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
            _id = doc.pop("_id", None)
            doc["id"] = _id
            parsed_doc = self.model.model_validate(doc)
            parsed_documents.append(parsed_doc)
        return parsed_documents

    def get_collection_count(self) -> int:
        try:
            return self.collection.count_documents({})
        except errors.PyMongoError as e:
            print(f"Error counting documents in MongoDB: {e}")
            raise

    def close(self) -> None:
        self.client.close()
        print("Closed MongoDB connection.")
