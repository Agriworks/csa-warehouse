from fastapi import APIRouter, HTTPException
from app.services.storage.mongodb_service import get_data_from_collection, get_dataset_rows, get_dataset_by_id, get_dataset_rows_by_dataset_id
from app.schemas.models import (
    Dataset, GetDatasetByIdRequest, GetDatasetByIdResponse, GetDatasetsResponse,
    DatasetInformation, DatasetInformationResponse, GetDatasetByIdDetailedResponse
)
from app.db.database import datasets_information_collection
import math

browser_router = APIRouter()


@browser_router.get("/get-datasets", response_model=DatasetInformationResponse)
async def get_datasets():
    raw_data = list(datasets_information_collection.find().limit(9))

    # Transform the data to include all fields from datasets-information collection
    transformed_data = []
    for item in raw_data:
        dataset_info = DatasetInformation(
            id=item["_id"],
            dataset_name=item.get("dataset_name", ""),
            description=item.get("description", ""),
            permission=item.get("permission", ""),
            dataset_type=item.get("dataset_type", ""),
            tags=item.get("tags", []),
            dataset_id=item.get("dataset_id", ""),
            file_id=item.get("file_id"),
            is_temporal=item.get("is_temporal", False),
            is_spatial=item.get("is_spatial", False),
            pulled_from_pipeline=item.get("pulled_from_pipeline", False),
            user_email=item.get("user_email", ""),
            user_name=item.get("user_name", ""),
            user_id=item.get("user_id"),
            created_at=item.get("created_at", ""),
            updated_at=item.get("updated_at", ""),
            pipeline_id=item.get("pipeline_id")
        )
        transformed_data.append(dataset_info)

    return DatasetInformationResponse(status="success", data=transformed_data)


@browser_router.post("/get-dataset-by-id", response_model=GetDatasetByIdDetailedResponse)
async def get_dataset_by_id_endpoint(request: GetDatasetByIdRequest):
    # First, find the dataset information using dataset_id
    dataset_info_doc = datasets_information_collection.find_one(
        {"dataset_id": request.dataset_id})
    if dataset_info_doc is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Create DatasetInformation object
    dataset_information = DatasetInformation(
        id=dataset_info_doc["_id"],
        dataset_name=dataset_info_doc.get("dataset_name", ""),
        description=dataset_info_doc.get("description", ""),
        permission=dataset_info_doc.get("permission", ""),
        dataset_type=dataset_info_doc.get("dataset_type", ""),
        tags=dataset_info_doc.get("tags", []),
        dataset_id=dataset_info_doc.get("dataset_id", ""),
        file_id=dataset_info_doc.get("file_id"),
        is_temporal=dataset_info_doc.get("is_temporal", False),
        is_spatial=dataset_info_doc.get("is_spatial", False),
        pulled_from_pipeline=dataset_info_doc.get(
            "pulled_from_pipeline", False),
        user_email=dataset_info_doc.get("user_email", ""),
        user_name=dataset_info_doc.get("user_name", ""),
        user_id=dataset_info_doc.get("user_id"),
        created_at=dataset_info_doc.get("created_at", ""),
        updated_at=dataset_info_doc.get("updated_at", ""),
        pipeline_id=dataset_info_doc.get("pipeline_id")
    )

    # Get the actual dataset data to get record count
    from app.db.database import datasets_collection
    dataset_doc = datasets_collection.find_one({"_id": request.dataset_id})
    if dataset_doc is None:
        raise HTTPException(status_code=404, detail="Dataset data not found")

    record_count = dataset_doc.get("record_count", 0)

    # Calculate pagination
    offset = request.page_number * request.limit

    # Get the paginated rows using the new function
    rows = get_dataset_rows_by_dataset_id(
        request.dataset_id, offset, request.limit)

    return GetDatasetByIdDetailedResponse(
        status="success",
        dataset_information=dataset_information,
        record_count=record_count,
        data=rows
    )
