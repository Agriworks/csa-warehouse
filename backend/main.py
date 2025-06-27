from fastapi import FastAPI, HTTPException, Query
from uuid import UUID
from models import User, Dataset, ApiResponse
from crud import (
    create_user, get_user, update_user, delete_user,
    create_dataset, get_dataset, delete_dataset
)
from minio_service import generate_presigned_url

app = FastAPI()

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
        raise HTTPException(status_code=404, detail="User not found or unchanged")
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
    url = generate_presigned_url(filename)
    return {"upload_url": url} 