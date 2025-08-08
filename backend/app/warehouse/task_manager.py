# Serves as the central execution controlelr in the application
# Decides how and where to execute tasks based on their definitions

import asyncio
from typing import Dict, Any
from app.warehouse.task_definitions import TASK_REGISTRY, TaskType
from services.cloud_functions.executor import submit_task, get_task_status

class TaskManager:
    def __init__(self):
        self.fargate_runner = None 

    # Execute a task based on its type
    # This method checks the task type and routes it to the appropriate execution method
    async def execute_task(self, task_name: str, params: Dict[str, Any]) -> Any:
        if task_name not in TASK_REGISTRY:
            raise ValueError(f"Task '{task_name}' is not registered.")
        
        task_def = TASK_REGISTRY[task_name]
        print(task_def) 
        
        if task_def.task_type == TaskType.LIGHTWEIGHT:
            return await self._execute_lightweight_task(task_def, params)
        elif task_def.task_type == TaskType.HEAVY:
            return await self._execute_heavy_task(task_def, params)
        else:
            raise ValueError(f"Unknown task type for task '{task_name}'.")
        
    async def _execute_lightweight_task(self, task_def, params):
        # Directly call the handler function for lightweight tasks
        param_values = list(params)
        exec_id = submit_task(
            func_name = task_def.name,
            param_values = param_values,
            param_types = [str(type(v).__name__) for v in param_values],
            return_type = task_def.return_type
        )
        return exec_id 
    
    async def _execute_heavy_task(self, task_def, params):
        # For heavy tasks, we might want to use a separate runner like Fargate
        if not self.fargate_runner:
            raise RuntimeError("Fargate runner is not initialized.")
        
        # Here we would submit the task to the Fargate runner
        raise NotImplementedError("Heavy task execution is not implemented yet.")