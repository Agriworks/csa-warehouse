import os
import requests
import pandas as pd
from minio import Minio 
from pymongo import MongoClient
from dotenv import load_dotenv
import io 

load_dotenv()

# ------------------ MongoDB Setup ------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/fastapi_db?authSource=admin")
client = MongoClient(MONGO_URI)
db = client["fastapi_db"]

users_collection = db["users"]
datasets_collection = db["datasets"]

# download a file from a URL and convert it to a pandas DataFrame
# Store the file in MongoDB and return the DataFrame
def download_and_store_file(file_url):
    try:
        response = requests.get(file_url) 
        print(response)
        response.raise_for_status()  # Raise an error for bad responses

        # Convert CSV to pandas DataFrame
        csv_content = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_content)) 
        records = df.to_dict(orient="records") 
        return records 
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

# Store file metadata in MongoDB
def store_file_metadata(filename, content_type, file_url):
    records = download_and_store_file(file_url) 
    if records is None:
        print("Failed to download or convert the file. Try looking at the URL accessibility.")
        return
    document = {
        "filename": filename,
        "type": content_type,
        "url": file_url,
        "data": records  
    }
    datasets_collection.insert_one(document)
