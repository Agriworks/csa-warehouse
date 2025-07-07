import inspect
from typing import Any, Callable, Dict, List, Optional

"""
Note - Keep in mind that the callable object that we find becomes
unusable if we pass it back from the function. There no specific 
reason why this shouldn't work but it doesn't.

"""


def get_param_type(param: Any) -> str:
    """Get the type of the parameter as a string

    Args:
        param (Any): The parameter to get the type of

    Returns:
        str: The type of the parameter as a string
    """
    return type(param).__name__


def _extract_type_string(param_type: inspect.Parameter) -> str:
    """Extract the type from the string "<class 'type'>"

    Args:
        string (str): The string to extract the type from

    Returns:
        str: The type as a string
    """
    return str(param_type).split()[1][1:-2]


def introspect_run_with_args(
    module: object,
    func_name: str,
    param_types: List[str],
    param_values: List[Any],
    retrun_type: str,
) -> Optional[Dict[str, Any]]:
    """Introspect the module and run the function reference

    Args:
        module (object): The module to introspect
        func_name (str): The name of the function to introspect
        param_types (List[str]): The types of the parameters
        retrun_type (str): The return type of the function

    Returns:
        Optional[object]: The function reference
    """
    for name, obj in inspect.getmembers(module):
        print(f"Name: {name}, Object: {obj}")
        if inspect.isfunction(obj):
            # print(inspect.isfunction(obj))
            signature = inspect.signature(obj)
            parameters = [
                _extract_type_string(param_signature.annotation)
                for _, param_signature in signature.parameters.items()
            ]

            # Converting the object <class return_type> into string
            return_type = signature.return_annotation

            # Extracting the 'return_type' from the converted string "<class 'return_type'>"
            return_type = _extract_type_string(return_type)

            print(f"Name: {name}, Parameters: {parameters}, Return Type: {retrun_type}")

            # If the function name is the same as the func_name, Run the function reference
            if name != func_name:
                continue
            if parameters != param_types:
                continue
            if retrun_type != retrun_type:
                continue
            result = obj(*param_values)

            return result
    return None


def introspect_run(module: object, func_name: str) -> None:
    """Introspect the module and return the function reference

    Args:
        module (object): The module to introspect
        func_name (str): The name of the function to introspect

    Returns:
        Optional[object]: The function reference
    """
    print("Searching for function: ", func_name)
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            print("Testing function: ", name)
            if name != func_name:
                continue

            if callable(obj) is False:
                print("Not callable: ", name)
                continue

            print("Found function: ", name)
            print("Running function: ", name)
            obj()
    return None