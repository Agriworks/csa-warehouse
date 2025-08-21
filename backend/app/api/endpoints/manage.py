from fastapi import APIRouter
from app.services.storage.mongodb_service import get_my_datasets
from app.schemas.models import (
    ManageDatasetResponse, GetMyDatasetsRequest, GetMyDatasetsResponse,
    DatasetInformation, DatasetInformationResponse
)

manage_router = APIRouter()


@manage_router.post("/get-my-datasets", response_model=DatasetInformationResponse)
async def get_my_datasets_endpoint(request: GetMyDatasetsRequest):
    raw_data = get_my_datasets(request.user_email)

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
