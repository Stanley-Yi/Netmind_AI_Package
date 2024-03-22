"""
=======
cot
=======
@file_name: cot.py
@author: Xiangpeng Wan
@date: 2024-3-22
"""
from xyz.node.agent import Agent
from xyz.parameters import openai_agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.utils.llm.openai_agent import OpenAIAgent
class Cot(Agent):
    def __init__(self):
        super().__init__(openai_agent)
        self.set_name("mathSolver")
        self.set_description("This is a teacher who can solve math questions.")
        self.set_parameters({"messages": {"type": "list", "description": "The OpenAI messages list which store the "
                                                                         "system message and user message"}
                             })
        self.openai_agent = OpenAIAgent(llm='gpt-4-0125-preview', temperature=0., top_p=1.0, max_tokens=2096)
        self.llm_cot_agent = LLMAgent(COTMATH, self.openai_agent, inner_multi=False, stream=True)
    def flowing(self,  messages: list) -> str:
        if messages is None:
            return self.llm_cot_agent(messages=messages)
COTMATH = {
    "system": """Now, you are a Mathematics assistant who can help user to solve the questions.
    """,
    "user": """
Hi, teacher. Please help me to summarize the history of dialogue. 
"""}