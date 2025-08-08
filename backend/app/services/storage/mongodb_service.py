import math 
from datetime import datetime, timezone
import pandas as pd
from typing import List
from app.db.database import datasets_collection

def store_to_mongodb(dataset_id: str, user_id: str, username: str, dataset_df: List[dict]) -> dict:

    wrapper_doc = {
        "_id": dataset_id,
        "user_id": user_id,
        "username": username,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(dataset_df),
        "data": dataset_df
    }

    result = datasets_collection.insert_one(wrapper_doc)

    return {
        "inserted_id": str(result.inserted_id),
        "record_count": len(dataset_df),
        "dataset_id": dataset_id,
        "ingested_at": wrapper_doc["ingested_at"]
    }

def sanitize_document(doc):
    def sanitize_value(value):
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None  # or use 0.0, depending on your use case
        elif isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(v) for v in value]
        return value

    doc["_id"] = str(doc["_id"])
    return {k: sanitize_value(v) for k, v in doc.items()}

def get_data_from_collection(collection = datasets_collection, limit: int = 9):
    try:
        documents = collection.find().limit(limit)
        return [sanitize_document(doc) for doc in documents]
    except Exception as e:
        raise RuntimeError(f"Error fetching documents: {e}")