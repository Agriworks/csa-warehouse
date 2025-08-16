from typing import List, Optional, Union, Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class Tag(BaseModel):
    """
    Tag object:
      - id: integer (int64)
      - name: string
    """
    id: int = Field(..., description="Unique identifier of the tag", example=123)
    name: str = Field(..., description="Name of the tag")


class User(BaseModel):
    """
    User object.
    """
    id: UUID = Field(..., description="Unique user ID (UUID)")
    username: Optional[str] = Field(None, description="Username")
    firstName: Optional[str] = Field(
        None, description="First name of the user")
    lastName: Optional[str] = Field(None, description="Last name of the user")
    email: Optional[str] = Field(
        None, description="Email address", example="name@email.com")
    organisation: Optional[str] = Field(
        None, description="Organisation of the user")


class Dataset(BaseModel):
    """
    Dataset object.
    """
    id: Optional[int] = Field(..., description="Unique dataset ID (int)")
    title: str = Field(..., description="Title of the dataset",
                       example="Soil Moisture Evolution in India")
    description: Optional[str] = Field(
        None, description="Text explaining what the dataset is about")
    uploader: User = Field(..., description="User who uploaded the dataset")
    uploadDate: datetime = Field(
        ...,
        description="The creation date and time in ISO 8601 format",
        example="2025-06-30T08:30:00Z"
    )
    tags: Optional[List[Tag]] = Field(
        None, description="List of tags associated with the dataset")
    isSpatial: bool = Field(...,
                            description="Whether the dataset has any geospatial identifiers")
    isTemporal: bool = Field(...,
                             description="Whether the dataset has any temporal identifiers")


class DatasetResponse(Dataset):
    document_id: str
    file_location: str


class ApiResponse(BaseModel):
    """
    Generic API response.
    """
    code: Optional[int] = Field(None, description="Response code", example=200)
    type: Optional[str] = Field(None, description="Type of response")
    message: Optional[str] = Field(
        None, description="Message accompanying the response")


class Error(BaseModel):
    """
    Error response object.
    """
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class CloudFunctionRequest(BaseModel):
    func_name: str
    param_values: List[Any]
    # param_types: List[str]
    # return_type: str


class RunPipelineRequest(BaseModel):
    dataset_id: str
    user_id: str
    username: str


class PipelineStatusRequest(BaseModel):
    dataset_id: str
    user_id: str

# Response models for pipeline endpoints


class RunPipelineResponse(BaseModel):
    """
    Response model for /run-pipeline endpoint
    """
    status: str = Field(..., description="The current status of the pipeline", enum=[
                        "running", "completed", "error"])


class PipelineStatusResponse(BaseModel):
    """
    Response model for /pipeline-status endpoint
    """
    status: str = Field(..., description="The current status of the pipeline", enum=[
                        "running", "completed", "error"])


class PipelineRunResponse(BaseModel):
    """
    Response model for /run endpoint
    """
    status: str = Field(..., description="The current status of the pipeline", enum=[
                        "running", "completed", "error"])


class Dataset(BaseModel):
    """
    Browse dataset response object with limited fields.
    """
    id: str = Field(..., description="Dataset ID")
    datasetname: str = Field(..., description="Name of the dataset")
    description: Optional[str] = Field(
        None, description="Description of the dataset")
    ingested_date: str = Field(...,
                               description="Date when the dataset was ingested")
    user_name: str = Field(...,
                           description="Name of the user who ingested the dataset")
    user_id: str = Field(...,
                         description="ID of the user who ingested the dataset")


class GetDatasetsResponse(BaseModel):
    """
    Browse API response wrapper.
    """
    status: str = Field(..., description="Response status")
    data: List[Dataset] = Field(...,
                                description="List of datasets")


class GetDatasetByIdRequest(BaseModel):
    """
    Request model for getting dataset rows with pagination.
    """
    id: str = Field(..., description="Dataset ID")
    offset: int = Field(0, description="Number of rows to skip", ge=0)
    limit: int = Field(
        10, description="Number of rows to return", ge=1, le=1000)


class GetDatasetByIdResponse(BaseModel):
    """
    Response model for dataset rows with metadata.
    """
    status: str = Field(..., description="Response status")
    id: str = Field(..., description="Dataset ID")
    dataset_name: str = Field(..., description="Name of the dataset")
    description: Optional[str] = Field(
        None, description="Description of the dataset")
    ingested_time: str = Field(...,
                               description="Time when the dataset was ingested")
    user_id: str = Field(...,
                         description="ID of the user who ingested the dataset")
    user_name: str = Field(...,
                           description="Name of the user who ingested the dataset")
    data_type: Optional[str] = Field(None, description="Type of the dataset")
    record_count: int = Field(...,
                              description="Total number of records in the dataset")
    data: List[dict] = Field(..., description="Array of row objects")


class GetMyDatasetsRequest(BaseModel):
    """
    Request model for manage endpoint to get user's datasets.
    """
    user_id: str = Field(...,
                         description="ID of the user whose datasets to retrieve")


class ManageDatasetResponse(BaseModel):
    """
    Manage dataset response object with limited fields.
    """
    id: str = Field(..., description="Dataset ID")
    datasetname: str = Field(..., description="Name of the dataset")
    description: Optional[str] = Field(
        None, description="Description of the dataset")
    ingested_date: str = Field(...,
                               description="Date when the dataset was ingested")
    user_name: str = Field(...,
                           description="Name of the user who ingested the dataset")
    user_id: str = Field(...,
                         description="ID of the user who ingested the dataset")


class GetMyDatasetsResponse(BaseModel):
    """
    Manage API response wrapper.
    """
    status: str = Field(..., description="Response status")
    data: List[ManageDatasetResponse] = Field(...,
                                              description="List of datasets")
