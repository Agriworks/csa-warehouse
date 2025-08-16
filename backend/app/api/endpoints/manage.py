from fastapi import APIRouter
from app.services.storage.mongodb_service import get_my_datasets
from app.schemas.models import ManageDatasetResponse, GetMyDatasetsRequest, GetMyDatasetsResponse

manage_router = APIRouter()


@manage_router.post("/get-my-datasets", response_model=GetMyDatasetsResponse)
async def get_my_datasets_endpoint(request: GetMyDatasetsRequest):
    raw_data = get_my_datasets(request.user_id)

    # Transform the data to match the new model
    transformed_data = []
    for item in raw_data:
        dataset = ManageDatasetResponse(
            id=item["_id"],
            datasetname=item["_id"],
            description='',
            ingested_date=item["ingested_at"],
            user_id=item["user_id"],
            user_name=item["username"],
        )
        transformed_data.append(dataset)

    return GetMyDatasetsResponse(status="success", data=transformed_data)
