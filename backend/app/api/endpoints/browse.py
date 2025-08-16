from fastapi import APIRouter, HTTPException
from app.services.storage.mongodb_service import get_data_from_collection, get_dataset_rows, get_dataset_by_id
from app.schemas.models import Dataset, GetDatasetByIdRequest, GetDatasetByIdResponse, GetDatasetsResponse

browser_router = APIRouter()


@browser_router.get("/get-datasets", response_model=GetDatasetsResponse)
async def get_datasets():
    raw_data = get_data_from_collection()

    # Transform the data to match the new model
    transformed_data = []
    for item in raw_data:
        dataset = Dataset(
            id=item["_id"],
            datasetname=item["_id"],
            description='',
            ingested_date=item["ingested_at"],
            user_id=item["user_id"],
            user_name=item["username"],
        )
        transformed_data.append(dataset)

    return GetDatasetsResponse(status="success", data=transformed_data)


@browser_router.post("/get-dataset-by-id", response_model=GetDatasetByIdResponse)
async def get_dataset_by_id_endpoint(request: GetDatasetByIdRequest):
    # Get the full dataset document to access metadata
    dataset_doc = get_dataset_by_id(request.id)
    if dataset_doc is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Get the paginated rows
    rows = get_dataset_rows(request.id, request.offset, request.limit)

    return GetDatasetByIdResponse(
        status="success",
        id=dataset_doc["_id"],
        dataset_name=dataset_doc["_id"],
        description="",
        ingested_time=dataset_doc["ingested_at"],
        user_id=dataset_doc["user_id"],
        user_name=dataset_doc["username"],
        data_type=None,
        record_count=dataset_doc["record_count"],
        data=rows
    )
