"""
Pipeline ID to Dataset Name mapping configuration.

This file contains mappings between pipeline IDs and their corresponding
dataset names in the ERP system. This is needed because the ERP system
uses specific dataset names, while our system uses pipeline IDs.
"""

# Mapping of pipeline IDs to ERP dataset names
PIPELINE_DATASET_MAPPING = {
    # Add your pipeline mappings here
    # "pipeline_id": "ERP Dataset Name"
    
    # Example mappings (replace with actual mappings)
    "soil_collection": "Soil Collection Data",
    "weather_data": "Weather Data",
    "crop_yield": "Crop Yield Data",
    
    # Add more mappings as needed
}

def get_dataset_name_for_pipeline(pipeline_id: str) -> str:
    """
    Get the ERP dataset name for a given pipeline ID.
    
    Args:
        pipeline_id: The pipeline ID to look up
        
    Returns:
        The corresponding dataset name, or the pipeline_id itself if no mapping exists
    """
    return PIPELINE_DATASET_MAPPING.get(pipeline_id, pipeline_id)
