import io 
import os
import requests
import pandas as pd
from pymongo import MongoClient
from ..config.settings import get_database_settings 

settings = get_database_settings() 

# ------------------ MongoDB Setup ------------------
MONGO_URI = str(settings.mongodb_uri)
client = MongoClient(MONGO_URI)
db = client["fastapi_db"]

users_collection = db["users"]
datasets_collection = db["datasets"] 

# New collection for pipeline status
pipeline_status = db["pipelineStatus"] 