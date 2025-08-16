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


def get_data_from_collection(collection=datasets_collection, limit: int = 9):
    try:
        documents = collection.find().limit(limit)
        return [sanitize_document(doc) for doc in documents]
    except Exception as e:
        raise RuntimeError(f"Error fetching documents: {e}")


def get_my_datasets(user_id: str, collection=datasets_collection, limit: int = 9):
    try:
        documents = collection.find({"user_id": user_id}).limit(limit)
        return [sanitize_document(doc) for doc in documents]
    except Exception as e:
        raise RuntimeError(f"Error fetching documents: {e}")


def get_dataset_by_id(dataset_id: str, collection=datasets_collection):
    try:
        document = collection.find_one({"_id": dataset_id})
        if document:
            return sanitize_document(document)
        return None
    except Exception as e:
        raise RuntimeError(f"Error fetching document: {e}")


def get_dataset_rows(dataset_id: str, offset: int = 0, limit: int = 10, collection=datasets_collection):
    try:
        document = collection.find_one({"_id": dataset_id})
        if not document:
            return None

        # Get the data array from the document
        data = document.get("data", [])

        # Apply pagination
        start_index = offset * limit
        end_index = start_index + limit

        # Return the paginated portion of the data
        paginated_data = data[start_index:end_index]

        return paginated_data
    except Exception as e:
        raise RuntimeError(f"Error fetching dataset rows: {e}")


def update_dataset_in_mongodb(dataset_id: str, user_id: str, username: str, dataset_df: List[dict]) -> dict:
    """Update an existing dataset with fresh data and updated timestamps"""

    wrapper_doc = {
        "user_id": user_id,
        "username": username,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(dataset_df),
        "data": dataset_df
    }

    result = datasets_collection.update_one(
        {"_id": dataset_id, "user_id": user_id},
        {"$set": wrapper_doc}
    )

    return {
        "updated_id": str(result.upserted_id) if result.upserted_id else dataset_id,
        "record_count": len(dataset_df),
        "dataset_id": dataset_id,
        "ingested_at": wrapper_doc["ingested_at"],
        "modified_count": result.modified_count
    }
