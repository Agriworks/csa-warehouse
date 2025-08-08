from app.warehouse.task_definitions import TaskDefinition, TaskType, register_task
from services.cloud_functions.server import custprocess

# Register the task
register_task(
    TaskDefinition(
        name = "function1",
        task_type = TaskType.LIGHTWEIGHT,
        description = "Concatenates two strings",
        module = custprocess,
        func_name = "func1",
        cpu_units = 256,
        memory_mb = 512,
        return_type = str
    )
)
