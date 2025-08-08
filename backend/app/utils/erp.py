import os
import json 
import pandas as pd
from dotenv import load_dotenv

from app.config.logging import get_logger, setup_logging
from erp_client.erp_next_client import ERPNextClient

setup_logging()
logger = get_logger("services.erp")
load_dotenv()

fields = ["naming_series","subject","customer","raised_by","status","priority","issue_type",
          "issue_split_from","description","service_level_agreement","response_by","response_by_variance",
          "agreement_status","resolution_by","resolution_by_variance","service_level_agreement_creation",
          "on_hold_since","total_hold_time","first_response_time","first_responded_on","avg_response_time",
          "resolution_details","opening_date","opening_time","resolution_date","resolution_time",""
          "user_resolution_time","lead","contact","email_account","customer_name","project","company",
          "via_customer_portal","attachment","content_type"]

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

def pull_dataset(dataset_name: str) -> pd.DataFrame:
    erp_uri = os.getenv("ERP_URI")
    erp_username = os.getenv("ERP_USERNAME")
    erp_password = os.getenv("ERP_PASSWORD")

    if not all([erp_uri, erp_username, erp_password]):
        raise ValueError("Missing required environment variables: ERP_URI, ERP_USERNAME, ERP_PASSWORD")

    try:
        logger.info(f"Connecting to ERP instance: {erp_uri}")
        client = ERPNextClient(base_url=erp_uri)

        client.login(username=erp_username, password=erp_password)
        logger.info("Successfully logged in to ERP")

        logger.info(f"Fetching dataset: {dataset_name}")
        dataset = client.get_dataset(dataset_name)
        logger.info(f"Dataset contents:\n{dataset.head()}")

        logger.info("Syncing dataset with selected fields from index 0...")
        sync_data = get_dataset_with_fields(client, dataset_name, fields = fields)
        logger.info(f"Synced data:\n{sync_data.head()}")

        # logger.info("Converting the data into json")
        # sync_data = sync_data.to_json(orient = "records")
        # sync_data = json.dumps(sync_data, indent = 2)

        return sync_data

    except Exception as e:
        logger.exception("Error while pulling dataset")
        raise


if __name__ == "__main__":
    pull_dataset("Soil Collection Data")
