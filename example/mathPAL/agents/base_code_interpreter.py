"""
==============
Base Code Interpreter
==============
@file_name: base_code_interpreter.py
@author: He Yan
@date: 2024-3-25
"""

from typing import Any
from xyz.utils.llm.dummy_llm import dummy_agent as default_agent
from xyz.node.agent import Agent
from textwrap import dedent
import func_timeout

class BaseCodeInterpreter(Agent):
    def __init__(self, core_agent=...) -> None:
        super().__init__(core_agent)

        self.set_name("BaseCodeInterpreter")
        self.set_description("This is a python code interpreter, which can execute the code within a given time limit and return the result or an error message.")
        self.set_parameters({
                "code": {
                    "type": "str",
                    "description": "The code need to be executed."
                },
                "keys": {
                    "type": "list",
                    "description": "The keys to be returned after executing the code."
                },
                "timeout_duration": {
                    "type": "int",
                    "description": "The maximum allowed time for the code to execute, in seconds."
                }
            })
    
    def flowing(self, code: str, keys=None, timeout_duration=5) -> Any:
        return execute_code(code, keys, timeout_duration)

def execute_code(code: str, keys=None, timeout_duration=5):
    """
    Executes the given code string and returns the result.

    Parameters
    ----------
    code : str
        The code string to be executed.
    keys : list, optional
        If provided, the function will return a list containing the values of each key after executing the code.
        If not provided, the function will return the value of a variable named 'ans', or None if it does not exist.
    timeout_duration : int, optional
        The maximum allowed time for the code to execute, in seconds. Defaults to 5 seconds.

    Returns
    -------
    result : any
        The result after executing the code. If the code executes successfully, the result is returned;
        if the code execution times out, the string "Error execution time exceeded the limit" is returned;
        if an error occurs during code execution, the string "Error during execution: {e}" is returned, where {e} is the error message.

    Raises
    ------
    Exception
        If an error occurs during code execution, an exception is raised.

    """
    def execute(x):
        try:
            local_namespace = {**locals(), **globals()}
            exec(x, local_namespace, local_namespace)
            if keys is None:
                return local_namespace.get('ans', None)
            else:
                return [local_namespace.get(k, None) for k in keys]
        except Exception as e:
            return f"Error in executing code: {e}"

    try:
        result = func_timeout.func_timeout(timeout_duration, execute, args=(code,))
    except func_timeout.FunctionTimedOut:
        result = "Error execution time exceeded the limit"
    except Exception as e:
        result = f"Error during execution: {e}"

    return result