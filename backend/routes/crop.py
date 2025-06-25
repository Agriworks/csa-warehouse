from fastapi import APIRouter, HTTPException
from database import db
from database import crop_data_collection

router = APIRouter()

@router.get("/crops/from_s3")
def get_crop_file_metadata():
    doc = crop_data_collection.find_one({"form": "Crop", "filename": "Crop.csv"}, {"_id": 0, "s3_url": 1})
    if not doc:
        raise HTTPException(status_code=404, detail="Crop file metadata not found")
    return doc  # returns { "s3_url": "..." }

@router.get("/crops/data")
def get_crop_data():
    doc = crop_data_collection.find_one({"form": "Crop", "filename": "Crop.csv"}, {"_id": 0, "data": 1})
    if not doc:
        raise HTTPException(status_code=404, detail="Crop data not found")
    return doc  # returns { "data": [...] }
