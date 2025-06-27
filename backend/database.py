from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["agriworks"]  # Make sure this matches your Atlas DB name!
users_collection = db["users"]
datasets_collection = db["datasets"]
crop_data_collection = db["crop_data"]  # Collection for crop data