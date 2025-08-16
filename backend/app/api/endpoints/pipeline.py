from fastapi import APIRouter
from app.utils.erp import pull_dataset
from app.schemas.models import PipelineStatusRequest, RunPipelineRequest, PipelineStatusResponse, RunPipelineResponse
from app.services.storage.mongodb_service import store_to_mongodb
from app.services.tasks.task_executor import submit_task, get_task_status

run_router = APIRouter()


@run_router.post("/run", response_model=RunPipelineResponse)
async def run_pipeline(request: RunPipelineRequest):
    dataset = pull_dataset(request.dataset_id)
    dataset_json = dataset.to_dict(orient="records")
    result = store_to_mongodb(
        request.dataset_id, request.user_id, request.username, dataset_json)
    return RunPipelineResponse(status="completed")


@run_router.post("/run-pipeline", response_model=RunPipelineResponse)
def run_pipeline(request: RunPipelineRequest):
    result, exec_id = submit_task(
        request.dataset_id, request.user_id, request.username)

    # Map "not found" to "error" for frontend compatibility
    status = result.get("Task Status", "running")
    if status == "not found":
        status = "error"

    return RunPipelineResponse(status=status)


@run_router.post("/pipeline-status", response_model=PipelineStatusResponse)
def get_pipeline_status(request: PipelineStatusRequest):
    result = get_task_status(request.dataset_id, request.user_id)
    task_status = result.get("Task Status", "not found")

    # Map "not found" to "error" for frontend compatibility
    if task_status == "not found":
        task_status = "error"

    return PipelineStatusResponse(status=task_status)
