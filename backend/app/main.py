from uuid import UUID
from io import BytesIO
from base64 import b64decode
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
# CloudFunctionRequest, DatasetResponse
from app.schemas.models import User, Dataset, ApiResponse
from app.db.crud import (
    create_user, get_user, update_user, delete_user,
    create_dataset, get_dataset, delete_dataset
)
from app.utils.file_utils import *
from app.services.storage.minio_service import get_minio_service
# from services.cloud_functions.server import introspection, custprocess
# from services.cloud_functions.executor import submit_task, get_task_status
# from app.warehouse.task_manager import TaskManager
# from app.services.cloud_functions.ETL_function import clean_csv
# from app.services.storage.minio_service import MinioStorageService
from app.api.endpoints.pipeline import run_router
from app.api.endpoints.browse import browser_router
from app.api.endpoints.manage import manage_router
# Register the tasks
# import app.warehouse.register_tasks

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(run_router)
app.include_router(browser_router)
app.include_router(manage_router)
# Initialize the Task Manager
# task_manager = TaskManager()

# User Routes


@app.post("/users/", response_model=ApiResponse)
def create_user_endpoint(user: User):
    create_user(user)
    return ApiResponse(code=201, type="success", message="User created")


@app.get("/users/{user_id}")
def get_user_endpoint(user_id: UUID):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=ApiResponse)
def update_user_endpoint(user_id: UUID, user: User):
    modified = update_user(user_id, user.model_dump(exclude={"id"}))
    if modified == 0:
        raise HTTPException(
            status_code=404, detail="User not found or unchanged")
    return ApiResponse(code=200, type="success", message="User updated")


@app.delete("/users/{user_id}", response_model=ApiResponse)
def delete_user_endpoint(user_id: UUID):
    deleted = delete_user(user_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return ApiResponse(code=200, type="success", message="User deleted")


# Dataset Routes

@app.post("/datasets/", response_model=ApiResponse)
def create_dataset_endpoint(dataset: Dataset):
    create_dataset(dataset)
    return ApiResponse(code=201, type="success", message="Dataset created")


@app.get("/datasets/{dataset_id}")
def get_dataset_endpoint(dataset_id: int):
    ds = get_dataset(dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds


@app.delete("/datasets/{dataset_id}", response_model=ApiResponse)
def delete_dataset_endpoint(dataset_id: int):
    deleted = delete_dataset(dataset_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ApiResponse(code=200, type="success", message="Dataset deleted")


@app.get("/generatePresignedURL")
def get_presigned_url(filename: str = Query(...)):
    minio_service = get_minio_service()
    url = minio_service.generate_presigned_url(filename)
    return {"upload_url": url}

# # Test Endpoint that don't run on a thread
# @app.post("/invoke-function")
# async def invoke_function(request: CloudFunctionRequest):
#     try:
#         result = introspection.introspect_run_with_args(
#             module = custprocess,
#             func_name = request.func_name,
#             param_values = request.param_values,
#             param_types = request.param_types,
#             retrun_type = request.return_type
#         )
#         if result is None:
#             raise HTTPException(status_code = 404, detail = "Function not found or failed to execute")
#         return {"status": "success", "data": result}
#     except Exception as e:
#         raise HTTPException(status_code = 500, detail = str(e))
# @app.post("/submit-task")
# async def submit_task_endpoint(request: CloudFunctionRequest):
#     try:
#         exec_id = await task_manager.execute_task(
#             task_name = request.func_name,
#             params = request.param_values
#         )
#         return {"status": "running", "exec_id": exec_id}
#     except ValueError as ve:
#         raise HTTPException(status_code = 400, detail = str(ve))

# @app.get("/task-status/{exec_id}")
# def get_task_status_endpoint(exec_id: str):
#     try:
#         status = get_task_status(exec_id)
#         if status["status"] == "not found":
#             raise HTTPException(status_code = 404, detail = "Task not found")
#         return status
#     except Exception as e:
#         raise HTTPException(status_code = 500, detail = str(e))
