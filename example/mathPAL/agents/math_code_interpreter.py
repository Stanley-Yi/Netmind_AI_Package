from typing import Any
from xyz.node.agent import Agent
from .base_code_interpreter import BaseCodeInterpreter
import re

class MathCodeInterpreter(Agent):
    def __init__(self, core_agent=...) -> None:
        super().__init__(core_agent)
        
        # 1. Set Agent attributes for building society in XYZ later version
        # For example, description might be used to show the assistant's function
        # in the society and guide a manager assistant to choose the right assistant.
        self.set_name("MathCodeInterpreter")
        self.set_description("This is a python code interpreter, which can execute the code to solve a math problem and finally return a numerical answer.")
        self.set_parameters({
                "code": {
                    "type": "str",
                    "description": "The code need to be executed."
                }
            })
    
        self.code_interpreter_agent = BaseCodeInterpreter()

    def flowing(self, code) -> int | float | None:
        ans = self.code_interpreter_agent(code=code, timeout_duration=5)
        if type(ans) is str:
            ans = simplify_ans(floatify_ans(ans), convert_to_str=True)
        return ans

def floatify_ans(ans):
    """
    Converts the input to a float, if possible.

    Parameters
    ----------
    ans : any
        The input to be converted to a float.

    Returns
    -------
    float or str or None
        The input converted to a float, if possible. If the input is a dictionary, the function attempts to convert the first value to a float.
        If the input is a list or tuple, the function attempts to convert the first element to a float.
        If the input is a string that contains a number, the function extracts the number and converts it to a float.
        If the input cannot be converted to a float, the function returns the input as a string or None if the input is empty.

    """
    if ans is None:
        return None
    elif type(ans) == dict:
        ans = list(ans.values())[0]
    elif type(ans) == bool:
        ans = ans
    elif type(ans) in [list, tuple]:
        if not ans:
            return None
        else:
            try:
                ans = float(ans[0])
            except Exception:
                ans = str(ans[0])
    else:
        try:
            ans = float(ans)
        except Exception:
            if "Error" not in ans:
                # 找到 ans 中的浮点数
                ans = re.findall(r"[-+]?\d*\.\d+|\d+", ans)
                if ans:
                    ans = float(ans[0])
                else:
                    ans = str(ans)
    return ans

def simplify_ans(ans, convert_to_str: bool = True):
    """
    Simplify the answer from a mathematical tools.

    Parameters
    ----------
    ans : various types
        The answer from a mathematical tools, could be various types (e.g., relational, numpy array, etc.)
    convert_to_str : bool, optional
        If True, convert the answer to string type. Default is True.

    Returns
    -------
    various types
        The simplified answer. The return type depends on the input and the `convert_to_str` parameter.
    """

    if 'relational' in str(type(ans)):
        return str(ans)
    elif 'numpy' in str(type(ans)):
        if ans.shape == ():
            # scalar value
            ans = round(float(ans), 2)
        else:
            # array value
            ans = round(float(ans[0]), 2)
        if convert_to_str:
            return str(ans)
        else:
            return ans
    elif not ans:
        return None
    else:
        if type(ans) in [list, tuple]:
            if 'sympy' in str(type(ans[0])):
                try:
                    ans = [round(float(x), 5) for x in ans]
                except Exception:
                    ans = [str(x) for x in ans]
            if len(ans) == 1:
                ans = ans[0]
        else:
            if 'sympy' in str(type(ans)):
                try:
                    ans = round(float(ans), 5)
                except Exception:
                    ans = str(ans)
        if convert_to_str:
            if type(ans) is str:
                return ans
            else:
                return str(round(ans, 5))
        else:
            return ans