import io
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from app.config.logging import get_logger
from app.db.database import datasets_collection
from app.services.storage.minio_service import MinioStorageService

logger = get_logger("csv_processor")


def extract_csv_data_from_minio(minio_service: MinioStorageService, filename: str) -> Optional[List[Dict[str, Any]]]:
    """
    Download CSV file from MinIO and extract its data as a list of dictionaries

    Args:
        minio_service: MinIO service instance
        filename: Name of the file in MinIO bucket

    Returns:
        List of dictionaries representing CSV rows, or None if processing fails
    """
    try:
        logger.info(f"Attempting to extract CSV data from file: {filename}")

        # Download the file from MinIO
        file_data = minio_service.client.get_object(
            minio_service.bucket, filename)
        csv_content = file_data.read().decode('utf-8')

        # Parse CSV content using pandas
        df = pd.read_csv(io.StringIO(csv_content))

        # Handle infinite and NaN values
        df = df.replace([np.inf, -np.inf], np.nan)

        # Clean data for JSON serialization
        records = df.to_dict(orient="records")

        # Additional cleaning to ensure JSON compatibility
        cleaned_records = []
        for record in records:
            cleaned_record = {}
            for key, value in record.items():
                # Handle various problematic values
                if pd.isna(value) or value is None:
                    cleaned_record[key] = None
                elif isinstance(value, (int, float)) and (np.isinf(value) or np.isnan(value)):
                    cleaned_record[key] = None
                else:
                    cleaned_record[key] = value
            cleaned_records.append(cleaned_record)

        records = cleaned_records

        logger.info(
            f"Successfully extracted {len(records)} records from CSV file: {filename}")
        return records

    except Exception as e:
        logger.error(
            f"Error extracting CSV data from {filename}: {str(e)}")
        return None


def store_csv_data_in_mongodb(filename: str, csv_data: List[Dict[str, Any]], user_id: str = None, username: str = None) -> Dict[str, Any]:
    """
    Store extracted CSV data in the datasets collection

    Args:
        filename: Name of the original file
        csv_data: List of dictionaries representing CSV rows
        user_id: Optional user ID
        username: Optional username

    Returns:
        Dictionary with dataset_id and columns array
    """
    try:
        logger.info(
            f"Storing CSV data in datasets collection for file: {filename}")

        import uuid
        from datetime import datetime, timezone

        # Generate UUID for the dataset
        dataset_uuid = str(uuid.uuid4())

        # Extract columns from the first row
        columns = list(csv_data[0].keys()) if csv_data else []

        document = {
            "_id": dataset_uuid,
            "data": csv_data,
            "columns": columns,
            "record_count": len(csv_data),
        }

        result = datasets_collection.insert_one(document)

        logger.info(
            f"CSV data stored in datasets collection with ID: {dataset_uuid}")

        return {
            "dataset_id": dataset_uuid,
            "columns": columns
        }

    except Exception as e:
        logger.error(
            f"Error storing CSV data in datasets collection: {str(e)}")
        raise


def get_csv_preview(filename: str, limit: int = 5) -> Optional[Dict[str, Any]]:
    """
    Get a preview of CSV data from MongoDB

    Args:
        filename: Name of the file
        limit: Number of rows to return in preview

    Returns:
        Dictionary with preview data or None if not found
    """
    try:
        document = datasets_collection.find_one({"filename": filename})

        if not document:
            return None

        data = document.get("data", [])
        preview_data = data[:limit] if data else []

        # Clean preview data for JSON serialization
        cleaned_preview = []
        for record in preview_data:
            cleaned_record = {}
            for key, value in record.items():
                if value is None or (isinstance(value, float) and (value != value or value == float('inf') or value == float('-inf'))):
                    cleaned_record[key] = None
                else:
                    cleaned_record[key] = value
            cleaned_preview.append(cleaned_record)

        return {
            "filename": filename,
            "total_records": len(data),
            "preview_records": len(preview_data),
            "columns": document.get("columns", []),
            "preview": cleaned_preview
        }

    except Exception as e:
        logger.error(f"Error getting CSV preview for {filename}: {str(e)}")
        return None
