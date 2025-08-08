# Simple task registry where developers can register tasks
# and their metadata for introspection and execution

from typing import Dict, Any, Callable
from enum import Enum 

# Define the types of tasks that can be registered
class TaskType(Enum):
    LIGHTWEIGHT = "lightweight"
    HEAVY = "heavy" 

# Define a structure for task definitions
# This includes metadata like name, type, description, handler function, and resource requirements
class TaskDefinition:
    def __init__(self, name: str, task_type: TaskType, description: str, 
                 module: str, func_name: str, cpu_units: int, memory_mb: int, return_type: Any = None):
        self.name = name
        self.task_type = task_type
        self.description = description
        self.module = module 
        self.func_name = func_name 
        self.cpu_units = cpu_units
        self.memory_mb = memory_mb 
        self.return_type = return_type  

# Registry to hold all task definitions
TASK_REGISTRY: Dict[str, TaskDefinition] = {} 

# Function to register a new task definition
def register_task(definition: TaskDefinition):
    if definition.name in TASK_REGISTRY:
        raise ValueError(f"Task '{definition.name}' is already registered.")
    TASK_REGISTRY[definition.name] = definition 

# Function to get all registered tasks
# This can be used to introspect available tasks in the system 
def get_registered_tasks() -> Dict[str, TaskDefinition]:
    return TASK_REGISTRY 

# Function to get a specific task definition by name 
def get_task_definition(task_name: str) -> TaskDefinition:
    """Get the task definition by name"""
    if task_name not in TASK_REGISTRY:
        raise ValueError(f"Task '{task_name}' is not registered.")
    return TASK_REGISTRY[task_name] 

