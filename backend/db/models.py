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
    firstName: Optional[str] = Field(None, description="First name of the user")
    lastName: Optional[str] = Field(None, description="Last name of the user")
    email: Optional[str] = Field(None, description="Email address", example="name@email.com")
    organisation: Optional[str] = Field(None, description="Organisation of the user")


class Dataset(BaseModel):
    """
    Dataset object.
    """
    id: Optional[int] = Field(..., description="Unique dataset ID (int)")
    title: str = Field(..., description="Title of the dataset", example="Soil Moisture Evolution in India")
    description: Optional[str] = Field(None, description="Text explaining what the dataset is about")
    uploader: User = Field(..., description="User who uploaded the dataset")
    uploadDate: datetime = Field(
        ...,
        description="The creation date and time in ISO 8601 format",
        example="2025-06-30T08:30:00Z"
    )
    tags: Optional[List[Tag]] = Field(None, description="List of tags associated with the dataset")
    isSpatial: bool = Field(..., description="Whether the dataset has any geospatial identifiers")
    isTemporal: bool = Field(..., description="Whether the dataset has any temporal identifiers")


class ApiResponse(BaseModel):
    """
    Generic API response.
    """
    code: Optional[int] = Field(None, description="Response code", example=200)
    type: Optional[str] = Field(None, description="Type of response")
    message: Optional[str] = Field(None, description="Message accompanying the response")


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