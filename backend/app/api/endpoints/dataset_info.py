from fastapi import APIRouter, HTTPException
from app.services.storage.mongodb_service import create_dataset_information
from app.schemas.models import (
    CreateDatasetInformationRequest,
    CreateDatasetInformationResponse,
    DatasetInformation
)

dataset_info_router = APIRouter()


@dataset_info_router.post("/create-dataset-information", response_model=CreateDatasetInformationResponse)
async def create_dataset_information_endpoint(request: CreateDatasetInformationRequest):
    """
    Create a new dataset information entry in the datasets-information collection.

    This endpoint allows users to manually create dataset information entries
    with all the required fields for tracking and managing datasets.
    """
    try:
        # Convert the request model to a dictionary
        dataset_info_data = request.model_dump()

        # Call the service function to create the dataset information
        result = create_dataset_information(dataset_info_data)

        if result["success"]:
            # Create the response with the created dataset information
            created_dataset_info = DatasetInformation(
                id=result["info_uuid"],
                dataset_name=request.dataset_name,
                description=request.description,
                permission=request.permission,
                dataset_type=request.dataset_type,
                tags=request.tags,
                dataset_id=request.dataset_id,
                file_id=request.file_id,
                is_temporal=request.is_temporal,
                is_spatial=request.is_spatial,
                pulled_from_pipeline=request.pulled_from_pipeline,
                user_email=request.user_email,
                user_name=request.user_name,
                user_id=request.user_id,
                created_at=result["created_at"],
                # Same as created_at for new entries
                updated_at=result["created_at"],
                pipeline_id=request.pipeline_id
            )

            return CreateDatasetInformationResponse(
                status="success",
                message=result["message"],
                data=created_dataset_info
            )
        else:
            # If creation failed, return error response
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
