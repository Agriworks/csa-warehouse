# Backend Development

## Overview
This repository contains backend components and services developed for data processing, orchestration, and API integration.  
The work includes dataset ingestion, ETL pipelines, API endpoints, and backend orchestration components.

```bash
poetry run uvicorn app.main:app # Run the backend
```

## API Endpoints

### POST `/run-dataset`

Triggers a pipeline execution for a given dataset ID. Stores execution metadata in the `pipeline_status` collection.

### Sample Request

```bash
curl -X POST "http://localhost:8000/run-dataset" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "dataset_123",
    "user_id": "example@gmail.com",
    "username": "example" 
  }'
```

### Request Body

```json
{
  "dataset_id": "dataset_123",
  "user_id": "example@gmail.com",
  "username": "example" 
}
```

### Sample Response

```json
{
    "status": "submitted",
    "execution_id": "f8347fe3-5391-4325-942d-252f53618271",
    "result": {
        "status": "running",
        "result": null, # You will see the results once its done
        "error": null
    }
}
```

---
### POST `/pipelineStatus`
Retrieves the status and results of a pipeline execution for a specific dataset and user.
### Sample Request
```bash
curl -X POST "http://localhost:8000/pipelineStatus" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "dataset_123",
    "user_id": "example@gmail.com"
  }'
```
### Request Body
```json
{
  "dataset_id": "dataset_123",
  "user_id": "example@gmail.com"
}
```
### Sample Response
```json
{
  "Task Status": "completed",
  "result": {
    "inserted_id": "dataset_123",
    "record_count": 10,
    "dataset_id": "dataset_123",
    "ingested_at": "2025-08-08T10:51:11.575039+00:00"
  },
  "error": null
}
```
---
### GET `/browse`
Retrieves and browses stored dataset information with detailed records.

### Sample Request

```bash
curl -X GET "http://localhost:8000/browse"
```

### Sample Response

```json
{
  "status": "success",
  "data": [
    {
      "_id": "dataset_123",
      "user_id": "example@gmail.com",
      "username": "example",
      "ingested_at": "2025-08-08T10:51:11.575039+00:00",
      "record_count": 10, 
      "data": [
        # Columns here
      ]
    }
  ]
}
```