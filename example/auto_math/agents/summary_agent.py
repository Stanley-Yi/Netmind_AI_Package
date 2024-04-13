""" 
============
SummaryAgent
============
@file_name: summary_agent.py
@author: Bin Liang
@date: 2024-04-13

"""


__all__ = ["SummaryAgent"]

from typing import Any

from xyz.node.agent import Agent  
from xyz.utils.llm.openai_client import OpenAIClient 
from xyz.node.basic.llm_agent import LLMAgent 


class SummaryAgent(Agent):
    
    def __init__(self, llm_client: OpenAIClient):
        super().__init__()
        
        self.set_information({
            "type": "function",
            "function": {
                "name": "SummaryAgent",
                "description": "This agent can help user to solve the question by using a plan.",
                "parameters": {"question": {"type": "str", "description": "The question here which need help."},
                               "answer": {"type": "str", "description": "The answer written by following the plan."},
                               "coding_result": {"type": "str", "description": "The result which be computed by the python code."}},
                "required": ["question", "answer", "coding_result"],
            },
        })
        
        self.llm_summary = LLMAgent(template=summary_prompt, llm_client=llm_client, stream=True)
        
    def flowing(self, question: str, answer: str, coding_answer: str) -> Any:
        
        return self.llm_summary(question=question, answer=answer, computed=coding_answer)
    
summary_prompt = [
{
"role": "system",
"content": """
Now, you are a Mathematics assistant who can help user to solve the questions. 

Requirements:
* You've got the question, and our original answer. Our original idea is correct, but there may be problems with the calculation. We use external tools to calculate the necessary content and the final answer. Your job is to compare the initial answer with the answer we calculated.
* If the original answer agrees with the calculated answer, summarize the answer to the question and make a reference answer for the question.
* If the original Aan and the calculated answer do not agree, then we consider the calculated answer to be more accurate. You need to replace the wrong part of the original answer with the calculated answer.
* Finally, summarize the answers and make a reference answer for the question.
* Maybe this problem is not a numerical calculation problem, if not, please ignore the calculation results.
* You have no need do more computing and check. We believe the calculated answer is the right final answer.
* You need to write out your thought process. When summarizing, you need to use a special format, "|||Summary: ", after which you write your reference answer.

Take a deep breath and start your work.
"""},
{
"role": "user",
"content": """
The question:
{question}
The original answer is:
{answer}
The computed answer is:
{computed}

Please help me to summarize the answer.
"""}]
        