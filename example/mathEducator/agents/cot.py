"""
=======
cot
=======
@file_name: cot.py
@author: Xiangpeng Wan
@date: 2024-3-22
"""
import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
print(sys.path)

from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.utils.llm.openai_agent import OpenAIAgent
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class Cot(Agent):
    def __init__(self):
        self.openai_agent = OpenAIAgent(api_key=OPENAI_API_KEY, model='gpt-4-0125-preview', temperature=0., top_p=1.0,
                                        max_tokens=2096)
        super().__init__(
            self.openai_agent)  # 这里需要传进去一个 xyz.utils.llm 里的语言模型，目前只有 openai（为了 之后的自驱动做准备，其实也并不是必须的。可以什么也不传。）

        self.set_name("mathSolver")
        self.set_description("This is a teacher who can solve math questions.")
        self.set_parameters({"question": {"type": "str", "description": "The question here which need help."}})

        self.llm_cot_agent = LLMAgent(COTMATH, self.openai_agent, inner_multi=False, stream=True)

    def flowing(self, question: str) -> str:
        response = self.llm_cot_agent(question=question)

        return response


# COTMATH = {
#     "system": """Now, you are a Mathematics assistant who can help user to solve the questions.
#     """,
#     "user": """
# Hi! Please solve this question:
#
# {question}
# """}

COTMATH = [
    {"role": "user", "content": """
    Hi! Please solve this question, I am xxx. 
    """},
    {"role": "system", "content": """Now, you are a Mathematics assistant who can help user to solve the questions."""},
    {"role": "user", "content": """
Hi! Please solve this question:

{question}  
"""}]
