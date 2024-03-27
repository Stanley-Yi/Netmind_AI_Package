"""
==============
Verify and vote
==============
@file_name: verify_and_vote.py
@author: He Yan
@date: 2024-3-25
"""

from typing import Any
from xyz.node.agent import Agent
from .base_code_interpreter import BaseCodeInterpreter

class VerifyAndVote(Agent):
    def __init__(self, core_agent=...) -> None:
        super().__init__(core_agent)
        
        # 1. Set Agent attributes for building society in XYZ later version
        # For example, description might be used to show the agent's function 
        # in the society and guide a manager agent to choose the right agent.
        self.set_name("VerifyAndVote")
        self.set_descriptions = ("This is a Python programming and math teacher tool designed to validate a list of answers"
                                    " for a math problem by executing a Python function named solution. It can also identify or"
                                    " select the most likely correct answer from the list.")
        self.set_parameters({
                "answers": {
                    "type": "list",
                    "description": "A list of answers need to be verified."
                },
                "code": {
                    "type": "str",
                    "description": "The code need to be executed."
                }
            })
        
        # 2. Initialize sub-agents for your custom agent
        # In your custom agent, you may integrate multiple other agents to achieve the goal.
        self.base_code_interpreter = BaseCodeInterpreter()
    
    def flowing(self, answers: list[str], code: str) -> str:
        verified_answers = []
        for ans in answers:
            # Step 1. The original code may lack the 'Verify' function.
            verify_code = add_verify_function(code, ans)
            # Step 2. Execute the code with the Verify function.
            try:
                result = self.base_code_interpreter(code=verify_code, timeout_duration=5)
                if result:
                    # Vote 2 times to make the result more reliable
                    verified_answers.extend([ans]*2)
                else:
                    verified_answers.append(ans)
            except:
                verified_answers.append(ans)
        # Step 3. Vote for the most likely correct answer.
        return vote(verified_answers)

def add_verify_function(code_string, value):
    if code_string.endswith(f"result = Verify({value})"):
        return code_string

    try:
        # 找到最后一个'\n'
        index = code_string.rfind('\n')
        # 删除index之后的内容
        code_string = code_string[:index]
        # 添加result = Verify(value)
        code_string = code_string + f"result = Verify({value})"
        return code_string
    except Exception as e:
        return f"Error during execution: {e}"

def auto_round(num_str):
    import re
    match = re.search(r'(\.(\d*?)(9{3,}|0{3,}|1{3,}|2{3,}|3{3,}|4{3,}|5{3,}|6{3,}|7{3,}|8{3,})\d*)', num_str)
    if match:
        precision = len(match.group(2))
        num = str(round(float(num_str), precision))
    else:
        num = num_str
    return num

def vote(values):
    # Vote counting
    vote_count = {}
    max_vote = 0
    max_value = "-5201314"
    for value in values:
        if not isinstance(value, str):
            value = str(value)
        vote_count[value] = vote_count.get(value, 0) + 1
        if vote_count[value] > max_vote:
            max_vote = vote_count[value]
            max_value = value

    max_value = auto_round(max_value)  # Round the value
    return max_value