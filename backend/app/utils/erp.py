import os
import json 
import pandas as pd
from dotenv import load_dotenv

from app.config.logging import get_logger, setup_logging
from app.config.pipeline_mapping import get_dataset_name_for_pipeline
from erp_client.erp_next_client import ERPNextClient

setup_logging()
logger = get_logger("services.erp")
load_dotenv()

def get_dataset_with_fields(client: ERPNextClient, dataset_id: str, fields: list = None, limit_page_length: int = 10) -> pd.DataFrame:
    if fields is None:
        fields = ["*"]
        
    endpoint = f"{client.base_url}/api/resource/{dataset_id}"
    fields_json = str(fields).replace("'", '"')

    params = {
        'limit_page_length': limit_page_length,
        'fields': json.dumps(fields),
    }

    response = client.session.get(endpoint, params=params)
    response.raise_for_status()

    records = response.json().get("data", [])
    return pd.DataFrame(records)

def pull_dataset(pipeline_id: str) -> pd.DataFrame:
    erp_uri = os.getenv("ERP_URI")
    erp_username = os.getenv("ERP_USERNAME")
    erp_password = os.getenv("ERP_PASSWORD")

    if not all([erp_uri, erp_username, erp_password]):
        raise ValueError("Missing required environment variables: ERP_URI, ERP_USERNAME, ERP_PASSWORD")

    # Map pipeline_id to actual dataset name
    dataset_name = get_dataset_name_for_pipeline(pipeline_id)
    logger.info(f"Mapped pipeline_id '{pipeline_id}' to dataset name '{dataset_name}'")

    try:
        logger.info(f"Connecting to ERP instance: {erp_uri}")
        client = ERPNextClient(base_url=erp_uri)

        client.login(username=erp_username, password=erp_password)
        logger.info("Successfully logged in to ERP")

        logger.info(f"Fetching dataset: {dataset_name}")
        try:
            dataset = client.get_dataset(dataset_name)
            logger.info(f"Dataset contents:\n{dataset.head()}")

            logger.info("Syncing dataset with selected fields from index 0...")
            sync_data = get_dataset_with_fields(client, dataset_name)
            logger.info(f"Synced data:\n{sync_data.head()}")

            return sync_data
        except Exception as dataset_error:
            if "404" in str(dataset_error) or "NOT FOUND" in str(dataset_error):
                logger.warning(f"Dataset '{dataset_name}' not found in ERP system. This might be expected for some datasets.")
                # Return empty DataFrame instead of raising error
                return pd.DataFrame()
            else:
                raise dataset_error

    except Exception as e:
        logger.exception("Error while pulling dataset")
        raise


if __name__ == "__main__":
    print(pull_dataset("Soil Collection Data"))
