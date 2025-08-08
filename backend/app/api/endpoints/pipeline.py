from fastapi import APIRouter, HTTPException
from app.utils.erp import pull_dataset
from app.schemas.models import RunPipeline
from app.services.storage.mongodb_service import store_to_mongodb

run_router = APIRouter()

@run_router.post("/run")
async def run_pipeline(request: RunPipeline):
    dataset = pull_dataset(request.dataset_id) 
    dataset_json = dataset.to_dict(orient="records")
    result = store_to_mongodb(request.dataset_id, dataset_json) 
    return {
        "status": "success",
        "result": result 
    }