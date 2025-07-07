import threading 
import uuid 
import os 
import sys 
from typing import Dict, Any 
from contextlib import redirect_stdout, redirect_stderr
from cloud_functions.rpc_server import introspection, custprocess

# Ensure the log directory exists
LOG_DIRS = "logs"
os.makedirs(LOG_DIRS, exist_ok = True)

# Dictionary to store task information
# Key: exec_id, Value: Dictionary with function details 
tasks: Dict[str, Dict[str, Any]] = {} 

# Function to handle task execution
def run_task(entrypoint, func_name, param_values, param_types, return_type, exec_id):
    """
    Execute a function in a separate thread and log the output.
    """
    # Create a unique log file for this execution
    log_file = os.path.join(LOG_DIRS, f"{exec_id}.log")
    with open(log_file, "w") as f, redirect_stdout(f), redirect_stderr(f):
        print(f"[Thread: {threading.current_thread().name}] Started task: {exec_id}") 
        try: 
            # Execute the function
            result = introspection.introspect_run_with_args(
                module = entrypoint,
                func_name = func_name,
                param_values = param_values,
                param_types = param_types,
                retrun_type = return_type
            )

            # Store the result in the tasks dictionary
            tasks[exec_id]["status"] = "completed"
            tasks[exec_id]["result"] = result
        except Exception as e:
            # Handle any exceptions that occur during execution
            print(f"Error during execution: {e}")
            tasks[exec_id]["status"] = "error"
            tasks[exec_id]["error"] = str(e)

# Function to submit a task for execution 
# This function generates a unique execution ID and starts a new thread to run the task.
# It returns the execution ID so that the client can check the status or result later.
def submit_task(func_name, param_values, param_types, return_type):
    """
    Submit a task for execution and return the execution ID.
    """
    # Generate a unique execution ID
    exec_id = str(uuid.uuid4())

    tasks[exec_id] = {
        "status": "running",
        "result": None,
    }

    thread = threading.Thread(
        target = run_task,
        args = (
            custprocess, 
            func_name, 
            param_values, 
            param_types, 
            return_type, 
            exec_id
        )
    ) 
    thread.start()
    return exec_id 

# Function to get the status of a task by its execution ID
# This function checks if the task exists and returns its status, result, error message, and log output.
# If the task does not exist, it returns a "not found" status.
def get_task_status(exec_id):
    """
    Get the status of a task by its execution ID.
    """
    # Check if the task exists
    task = tasks.get(exec_id)
    if not task:
        return {"status": "not found"}
    
    # Read the log file for this execution
    log_path = os.path.join(LOG_DIRS, f"{exec_id}.log") 
    log = "" 
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log = f.read() 

    return {
        "status": task["status"],
        "result": task.get("result"),
        "error": task.get("error"),
        "log": log 
    }