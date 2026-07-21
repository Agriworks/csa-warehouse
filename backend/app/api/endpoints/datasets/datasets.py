import os
import uuid
import mimetypes
import pandas as pd
from io import BytesIO
from datetime import datetime, timezone
from pymongo.collection import Collection
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.auth.user_auth import get_current_user
from app.schemas.models import (
    CreateDatasetInformationRequest,
    CreateDatasetInformationResponse,
    PresignedURLResponse,
    ExtractCsvDataRequest,
    ExtractAndStoreResponse,
    DatasetColumnsResponse,
    DatasetColumnsRequest,
)
from app.db.database import files as files_collection, datasets_collection, dataset_information_collection
from app.services.storage.mongodb_service import store_to_mongodb
from app.services.storage.storage_factory import get_storage_service

datasets_router = APIRouter()


@datasets_router.get("/presignedURL", response_model=PresignedURLResponse, operation_id="get_presigned_url")
def get_presigned_url(filename: str, current_user: dict = Depends(get_current_user)) -> PresignedURLResponse:
    storage_service = get_storage_service()
    user_id = str(current_user.get("_id"))
    url, object_name = storage_service.generate_presigned_url(
        filename=filename, user_id=user_id)
    return PresignedURLResponse(upload_url=url, object_name=object_name)


@datasets_router.post("/upload", response_model=PresignedURLResponse, operation_id="upload_dataset_file")
async def upload_dataset_file(
    files: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
) -> PresignedURLResponse:
    try:
        storage_service = get_storage_service()
        user_id = str(current_user.get("_id"))
        
        # Read file content
        file_content = await files.read()
        
        # Generate the unique filename using identical logic as MinioStorageService
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, extension = os.path.splitext(files.filename)
        new_filename = f"{name}_{timestamp}{extension}"
        
        if user_id:
            object_name = f"{user_id}/{new_filename}"
        else:
            object_name = new_filename
            
        # Upload the file directly to storage
        storage_service.upload_file(file_content, object_name)
        
        return PresignedURLResponse(upload_url="", object_name=object_name)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload file to storage: {str(e)}"
        )


@datasets_router.post("/datasets/create", response_model=CreateDatasetInformationResponse, operation_id="create_dataset")
async def create_dataset(request: CreateDatasetInformationRequest, current_user: dict = Depends(get_current_user)) -> CreateDatasetInformationResponse:
    try:
        dataset_doc = datasets_collection.find_one(
            {"_id": ObjectId(request.dataset_id)})

        if not dataset_doc:
            raise HTTPException(
                status_code=404, detail="Dataset not found in datasets_collection")

        dataset_info = {
            "_id": ObjectId(),
            "dataset_id": ObjectId(request.dataset_id),
            "file_id": ObjectId(request.file_id) if request.file_id else None,
            "dataset_name": request.dataset_name,
            "description": request.description,
            "permission": request.permission,
            "dataset_type": request.dataset_type,
            "tags": request.tags,
            "is_temporal": request.is_temporal,
            "is_spatial": request.is_spatial,
            "temporal_granularities": request.temporal_granularities,
            "spatial_granularities": request.spatial_granularities,
            "location_columns": request.location_columns,
            "time_columns": request.time_columns,
            "pulled_from_pipeline": False,
            "pipeline_id": None,  # null for manual datasets
            "user_id": [ObjectId(current_user.get("_id"))],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        dataset_information_collection.insert_one(dataset_info)

        return CreateDatasetInformationResponse(status="success", id=str(dataset_info["_id"]))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@datasets_router.post("/datasets/extract", response_model=ExtractAndStoreResponse, operation_id="extract_dataset")
def extract_csv(request: ExtractCsvDataRequest, current_user: dict = Depends(get_current_user)) -> ExtractAndStoreResponse:
    new_file_id = ObjectId()
    dataset_id = ObjectId()
    storage_service = get_storage_service()

    response = storage_service.get_object(object_name=request.file_object)
    if not response:
        raise HTTPException(status_code=404, detail="File not found in storage backend")

    file_content = response.read()
    file_type = mimetypes.guess_type(request.file_object)[
        0] or "application/octet-stream"
    file_size = len(file_content)

    response.close()
    response.release_conn()

    current_time = datetime.now(timezone.utc).isoformat()
    file_metadata = {
        "_id": new_file_id,
        "file_location": request.file_object,
        "file_type": file_type,
        "file_size": file_size,
        "user_id": current_user.get("_id"),
        "created_at": current_time,
        "updated_at": current_time,
    }

    files_collection.insert_one(file_metadata)

    try:
        df = pd.read_csv(BytesIO(file_content))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error parsing CSV: {str(e)}")

    dataset_records = df.to_dict(orient="records")
    current_time = datetime.now(timezone.utc).isoformat()
    datasets_collection.insert_one(
        {
            "_id": ObjectId(dataset_id),
            "data": dataset_records,
            "columns": df.columns.to_list(),
            "record_count": len(dataset_records),
            "created_at": current_time,
            "updated_at": current_time,
        }
    )

    return ExtractAndStoreResponse(status="success", file_id=str(new_file_id), dataset_id=str(dataset_id))


@datasets_router.get("/datasets/columns", response_model=DatasetColumnsResponse, operation_id="get_dataset_columns")
def get_dataset_columns(dataset_id: str, search: str = None, current_user: dict = Depends(get_current_user)) -> DatasetColumnsResponse:
    # Fetch dataset metadata
    dataset = datasets_collection.find_one({"_id": dataset_id})
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    all_columns = dataset.get("columns", [])

    # Apply filtering if search is provided
    if search:
        filtered = [col for col in all_columns if search.lower()
                    in col.lower()]
        filtered = filtered[:10]
        return DatasetColumnsResponse(columns=filtered)
    return DatasetColumnsResponse(columns=all_columns[:10])
