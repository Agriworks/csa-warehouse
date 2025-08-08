from datetime import datetime, timezone
import pandas as pd
from typing import List
from app.db.database import datasets_collection

def store_to_mongodb(dataset_id: str, dataset_df: List[dict]) -> dict:

    wrapper_doc = {
        "dataset_id": dataset_id,
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
