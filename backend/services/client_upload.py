import requests
import mimetypes
from db.database import store_file_metadata, MONGO_URI

def get_presigned_url(filename: str):
    response = requests.get("http://localhost:8000/generatePresignedURL", params={"filename": filename})
    return response.json()["upload_url"] 

def upload_file_to_presigned_url(file_path: str):
    filename = file_path.split("/")[-1]
    upload_url = get_presigned_url(filename)
    
    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or "application/octet-stream"
    
    with open(file_path, "rb") as f:
        response = requests.put(upload_url, data=f, headers={"Content-Type": mime_type})
    
    if response.status_code == 200:
        print("Upload successful!")
        store_file_metadata(filename, mime_type, upload_url.split("?")[0])
        print("File URL (MinIO):", upload_url.split("?")[0]) 
    else:
        print("Upload failed with code:", response.status_code)
        print(response.text)

upload_file_to_presigned_url("test.csv")