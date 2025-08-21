import math
import uuid
from datetime import datetime, timezone
import pandas as pd
from typing import List
from app.db.database import datasets_collection, datasets_information_collection


def store_to_mongodb(pipeline_id: str, username: str, user_email: str, dataset_df: List[dict]) -> dict:
    # Generate UUID for the dataset
    dataset_uuid = str(uuid.uuid4())

    # Store actual data in datasets collection with UUID
    dataset_doc = {
        "_id": dataset_uuid,
        "data": dataset_df,
        "columns": [],  # Empty array as requested
        "record_count": len(dataset_df)
    }

    # Store metadata in datasets-information collection
    dataset_info_doc = {
        "_id": str(uuid.uuid4()),  # Generate new UUID for info collection
        "dataset_name": f"{pipeline_id}",
        "description": f"Dataset extracted from pipeline_id: {pipeline_id} for {username}",
        "permission": "public",
        "dataset_type": "",
        "tags": [],
        "dataset_id": dataset_uuid,  # Reference to the UUID from datasets collection
        "file_id": None,
        "is_temporal": False,
        "is_spatial": False,
        "pulled_from_pipeline": True,
        "user_email": user_email,
        "user_name": username,
        "user_id": None,  # Keep for backward compatibility but set to None
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_id": pipeline_id  # Store the original pipeline_id
    }

    # Insert both documents
    dataset_result = datasets_collection.insert_one(dataset_doc)
    info_result = datasets_information_collection.insert_one(dataset_info_doc)

    return {
        "inserted_id": str(dataset_result.inserted_id),
        "dataset_uuid": dataset_uuid,
        "info_uuid": str(info_result.inserted_id),
        "record_count": len(dataset_df),
        "pipeline_id": pipeline_id,
        "created_at": dataset_info_doc["created_at"]
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


def get_my_datasets(user_email: str, collection=datasets_collection, limit: int = 9):
    try:
        # Query the datasets-information collection for user's datasets
        documents = datasets_information_collection.find(
            {"user_email": user_email}).limit(limit)
        return [sanitize_document(doc) for doc in documents]
    except Exception as e:
        raise RuntimeError(f"Error fetching documents: {e}")


def get_dataset_by_id(pipeline_id: str, collection=datasets_collection):
    try:
        # First, find the dataset information using pipeline_id
        info_document = datasets_information_collection.find_one(
            {"pipeline_id": pipeline_id})

        if not info_document:
            return None

        # This is the UUID from datasets collection
        dataset_uuid = info_document.get("dataset_id")
        if not dataset_uuid:
            return None

        # Now find the actual dataset data using the UUID
        document = datasets_collection.find_one({"_id": dataset_uuid})

        if not document:
            return None

        # Combine the information and data
        combined_doc = {
            **info_document,
            "data": document.get("data", []),
            "columns": document.get("columns", []),
            "record_count": document.get("record_count", 0)
        }

        return sanitize_document(combined_doc)
    except Exception as e:
        raise RuntimeError(f"Error fetching document: {e}")


def get_dataset_rows_by_dataset_id(dataset_id: str, offset: int = 0, limit: int = 10, collection=datasets_collection):
    try:
        # Find the actual dataset data directly using the dataset_id (UUID)
        document = datasets_collection.find_one({"_id": dataset_id})

        if not document:
            return None

        # Get the data array from the document
        data = document.get("data", [])

        # Apply pagination
        start_index = offset
        end_index = start_index + limit

        # Return the paginated portion of the data
        paginated_data = data[start_index:end_index]

        return paginated_data
    except Exception as e:
        raise RuntimeError(f"Error fetching dataset rows: {e}")


def get_dataset_rows(pipeline_id: str, offset: int = 0, limit: int = 10, collection=datasets_collection):
    try:
        # First, find the dataset information using pipeline_id
        info_document = datasets_information_collection.find_one(
            {"pipeline_id": pipeline_id})

        if not info_document:
            return None

        # This is the UUID from datasets collection
        dataset_uuid = info_document.get("dataset_id")
        if not dataset_uuid:
            return None

        # Now find the actual dataset data using the UUID
        document = datasets_collection.find_one({"_id": dataset_uuid})

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


def update_dataset_in_mongodb(pipeline_id: str, username: str, user_email: str, dataset_df: List[dict]) -> dict:
    """Update an existing dataset with fresh data and updated timestamps"""

    # First, find the existing dataset information using pipeline_id and user_email
    existing_info = datasets_information_collection.find_one(
        {"pipeline_id": pipeline_id, "user_email": user_email})

    if not existing_info:
        # If no existing info found, create new entries
        return store_to_mongodb(pipeline_id, username, user_email, dataset_df)

    # This is the UUID from datasets collection
    dataset_uuid = existing_info.get("dataset_id")

    # Update the actual data in datasets collection
    dataset_doc = {
        "data": dataset_df,
        "columns": [],  # Empty array as requested
        "record_count": len(dataset_df)
    }

    dataset_result = datasets_collection.update_one(
        {"_id": dataset_uuid},
        {"$set": dataset_doc}
    )

    # Update metadata in datasets-information collection with updated_at timestamp
    current_time = datetime.now(timezone.utc).isoformat()
    info_update_doc = {
        "updated_at": current_time
    }

    info_result = datasets_information_collection.update_one(
        {"pipeline_id": pipeline_id, "user_email": user_email},
        {"$set": info_update_doc}
    )

    return {
        "updated_id": dataset_uuid,
        "record_count": len(dataset_df),
        "pipeline_id": pipeline_id,
        "updated_at": current_time,
        "modified_count": dataset_result.modified_count,
        "info_modified_count": info_result.modified_count
    }


def create_dataset_information(dataset_info_data: dict) -> dict:
    """
    Create a new dataset information entry in the datasets-information collection.

    Args:
        dataset_info_data: Dictionary containing dataset information fields

    Returns:
        Dictionary with the result of the operation
    """
    try:
        from datetime import datetime, timezone

        # Generate UUID for the dataset information
        info_uuid = str(uuid.uuid4())

        # Prepare the document with current timestamps
        dataset_info_doc = {
            "_id": info_uuid,
            "dataset_name": dataset_info_data["dataset_name"],
            "description": dataset_info_data.get("description", ""),
            "permission": dataset_info_data["permission"],
            "dataset_type": dataset_info_data["dataset_type"],
            "tags": dataset_info_data.get("tags", []),
            "dataset_id": dataset_info_data["dataset_id"],
            "file_id": dataset_info_data["file_id"],
            "is_temporal": dataset_info_data["is_temporal"],
            "is_spatial": dataset_info_data["is_spatial"],
            "pulled_from_pipeline": dataset_info_data.get("pulled_from_pipeline", False),
            "user_email": dataset_info_data["user_email"],
            "user_name": dataset_info_data["user_name"],
            "user_id": dataset_info_data.get("user_id"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline_id": dataset_info_data.get("pipeline_id")
        }

        # Insert the document into the datasets-information collection
        result = datasets_information_collection.insert_one(dataset_info_doc)

        if result.inserted_id:
            return {
                "success": True,
                "message": "Dataset information created successfully",
                "info_uuid": str(result.inserted_id),
                "created_at": dataset_info_doc["created_at"]
            }
        else:
            return {
                "success": False,
                "message": "Failed to create dataset information"
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating dataset information: {str(e)}"
        }


def create_file_information(file_data: dict) -> dict:
    """
    Create a new file information entry in the files collection.

    Args:
        file_data: Dictionary containing file information fields

    Returns:
        Dictionary with the result of the operation
    """
    try:
        from datetime import datetime, timezone

        # Generate UUID for the file
        file_uuid = str(uuid.uuid4())

        # Prepare the document with current timestamps
        file_doc = {
            "_id": file_uuid,
            "file_ext": file_data["file_ext"],
            "file_name": file_data["file_name"],
            "file_size": file_data["file_size"],
            "file_type": file_data["file_type"],
            "file_url": file_data["file_url"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        # Import the files collection
        from app.db.database import files_collection

        # Insert the document into the files collection
        result = files_collection.insert_one(file_doc)

        if result.inserted_id:
            return {
                "success": True,
                "message": "File information created successfully",
                "file_uuid": str(result.inserted_id),
                "created_at": file_doc["created_at"]
            }
        else:
            return {
                "success": False,
                "message": "Failed to create file information"
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating file information: {str(e)}"
        }
