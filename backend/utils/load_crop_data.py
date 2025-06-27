import pandas as pd
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from io import StringIO
from datetime import datetime

load_dotenv()

CROP_CSV_URL = "http://localhost:9000/erp-data/Crop.csv"
FILENAME = "Crop.csv"

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["agriworks"]
collection = db["crop_data"]

# Step 1: Download the CSV file from MinIO
print(f"📥 Fetching: {CROP_CSV_URL}")
response = requests.get(CROP_CSV_URL)
response.raise_for_status()

# Step 2: Load the CSV into pandas
df = pd.read_csv(StringIO(response.text))
records = df.to_dict(orient="records")

# Step 3: Create the full document
collection.delete_many({})  # clear old flat records

document = {
    "form": "Crop",
    "filename": "Crop.csv",
    "s3_url": "http://localhost:9000/erp-data/Crop.csv",
    "data": records,
    "uploaded_at": datetime.utcnow()
}

collection.insert_one(document)

# Step 4: Insert or update in MongoDB
collection.replace_one(
    {"form": "Crop", "filename": FILENAME},
    document,
    upsert=True
)

print(f"✅ Uploaded {len(records)} crop records into MongoDB with metadata.")
