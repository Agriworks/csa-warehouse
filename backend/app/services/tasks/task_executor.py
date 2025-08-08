import threading
import uuid
from typing import Dict, Any

from app.utils.erp import pull_dataset
from app.services.storage.mongodb_service import store_to_mongodb
from app.config.logging import LoggerMixin

from app.db.database import pipeline_status, datasets_collection

# In-memory store for task metadata
tasks: Dict[str, Dict[str, Any]] = {}


class TaskRunner(LoggerMixin):
    def run_pipeline_task(self, dataset_id: str, user_id: str, username: str, exec_id: str):
        self.logger.info(f"[Thread: {threading.current_thread().name}] Starting task {exec_id} for dataset {dataset_id}")

        try:
            dataset = pull_dataset(dataset_id) 
            self.logger.info(f"[{exec_id}] Pulled dataset with {len(dataset)} records.")

            dataset_json = dataset.to_dict(orient="records")

            result = store_to_mongodb(dataset_id, user_id, username, dataset_json)
            self.logger.info(f"[{exec_id}] Dataset stored successfully in MongoDB.")

            tasks[exec_id]["Task Status"] = "completed"
            tasks[exec_id]["result"] = result

        except Exception as e:
            self.logger.error(f"[{exec_id}] Task failed with error: {e}", exc_info=True)
            tasks[exec_id]["Task Status"] = "error"
            tasks[exec_id]["error"] = str(e)

task_runner = TaskRunner()

def submit_task(dataset_id: str, user_id: str, username: str) -> str:

    existing_dataset = datasets_collection.find_one({"_id": dataset_id, "user_id": user_id})
    if existing_dataset:
        return {"error": f"Dataset with id '{dataset_id}' for user '{user_id}' already exists in the database"}, None

    exec_id = str(uuid.uuid4())
    wrapper_doc = {
        "_id": dataset_id, 
        "user_id": user_id, 
        "execution_id": exec_id
    }
    pipeline_status.insert_one(wrapper_doc) 

    tasks[exec_id] = {
        "Task Status": "running",
        "result": None,
        "error": None
    }

    thread = threading.Thread(
        target = task_runner.run_pipeline_task,
        args = (dataset_id, user_id, username, exec_id),
        name = f"TaskThread-{exec_id[:8]}"
    )
    
    thread.start()

    return tasks[exec_id], exec_id

def get_task_status(dataset_id: str, user_id: str) -> Dict[str, Any]:
    result = pipeline_status.find_one({"_id": dataset_id, "user_id": user_id})
    if not result:
        return {"Task Status": "not found", "message": "No matching dataset for this user."}

    exec_id = result.get("execution_id")
    if not exec_id:
        return {"Task Status": "error", "message": "Execution ID not found in pipeline status."}

    task = tasks.get(exec_id)
    if not task:
        return {"Task Status": "not found", "message": "Task not found in active task store."}

    return {
        "Task Status": task.get("Task Status"),
        "result": task.get("result"),
        "error": task.get("error")
    }
