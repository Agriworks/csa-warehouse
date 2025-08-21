import threading
import uuid
from typing import Dict, Any

from app.utils.erp import pull_dataset
from app.services.storage.mongodb_service import store_to_mongodb, update_dataset_in_mongodb
from app.config.logging import LoggerMixin

from app.db.database import pipeline_status, datasets_collection, datasets_information_collection

# In-memory store for task metadata
tasks: Dict[str, Dict[str, Any]] = {}


class TaskRunner(LoggerMixin):
    def run_pipeline_task(self, pipeline_id: str, username: str, user_email: str, exec_id: str, is_update: bool = False):
        self.logger.info(
            f"[Thread: {threading.current_thread().name}] Starting task {exec_id} for pipeline {pipeline_id} (update: {is_update})")

        try:
            dataset = pull_dataset(pipeline_id)
            self.logger.info(
                f"[{exec_id}] Pulled dataset with {len(dataset)} records.")

            dataset_json = dataset.to_dict(orient="records")

            if is_update:
                result = update_dataset_in_mongodb(
                    pipeline_id, username, user_email, dataset_json)
                self.logger.info(
                    f"[{exec_id}] Dataset updated successfully in MongoDB.")
            else:
                result = store_to_mongodb(
                    pipeline_id, username, user_email, dataset_json)
                self.logger.info(
                    f"[{exec_id}] Dataset stored successfully in MongoDB.")

            tasks[exec_id]["Task Status"] = "completed"
            tasks[exec_id]["result"] = result

        except Exception as e:
            self.logger.error(
                f"[{exec_id}] Task failed with error: {e}", exc_info=True)
            tasks[exec_id]["Task Status"] = "error"
            tasks[exec_id]["error"] = str(e)


task_runner = TaskRunner()


def submit_task(pipeline_id: str, username: str, user_email: str) -> tuple[Dict[str, Any], str]:
    # Check if dataset exists for the same user and pipeline_id
    existing_dataset = datasets_information_collection.find_one(
        {"pipeline_id": pipeline_id, "user_email": user_email})

    is_update = existing_dataset is not None

    exec_id = str(uuid.uuid4())
    wrapper_doc = {
        "_id": pipeline_id,
        "user_email": user_email,
        "execution_id": exec_id
    }

    # Update or insert pipeline status
    pipeline_status.update_one(
        {"_id": pipeline_id, "user_email": user_email},
        {"$set": wrapper_doc},
        upsert=True
    )

    tasks[exec_id] = {
        "Task Status": "running",
        "result": None,
        "error": None
    }

    thread = threading.Thread(
        target=task_runner.run_pipeline_task,
        args=(pipeline_id, username, user_email, exec_id, is_update),
        name=f"TaskThread-{exec_id[:8]}"
    )

    thread.start()

    return tasks[exec_id], exec_id


def get_task_status(pipeline_id: str, user_email: str) -> Dict[str, Any]:
    result = pipeline_status.find_one(
        {"_id": pipeline_id, "user_email": user_email})
    if not result:
        return {"Task Status": "not found", "message": "No matching pipeline for this user."}

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
