from fastapi import APIRouter, HTTPException
from app.services.storage.mongodb_service import create_file_information
from app.schemas.models import (
    CreateFileRequest,
    CreateFileResponse,
    FileInformation
)

files_router = APIRouter()


@files_router.post("/create-file", response_model=CreateFileResponse)
async def create_file_endpoint(request: CreateFileRequest):
    """
    Create a new file information entry in the files collection.

    This endpoint allows users to create file information entries
    with all the required fields for tracking and managing files.
    """
    try:
        # Convert the request model to a dictionary
        file_data = request.model_dump()

        # Call the service function to create the file information
        result = create_file_information(file_data)

        if result["success"]:
            # Create the response with the created file information
            created_file_info = FileInformation(
                id=result["file_uuid"],
                file_ext=request.file_ext,
                file_name=request.file_name,
                file_size=request.file_size,
                file_type=request.file_type,
                file_url=request.file_url,
                created_at=result["created_at"],
                # Same as created_at for new entries
                updated_at=result["created_at"]
            )

            return CreateFileResponse(
                status="success",
                message=result["message"],
                data=created_file_info
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
