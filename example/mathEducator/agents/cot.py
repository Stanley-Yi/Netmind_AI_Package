"""
=======
cot
=======
@file_name: cot.py
@author: Xiangpeng Wan
@date: 2024-3-22
"""


from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.utils.llm.openai_agent import OpenAIAgent


class Cot(Agent):
    def __init__(self):
        
        self.openai_agent = OpenAIAgent(model='gpt-4-0125-preview', temperature=0., top_p=1.0, max_tokens=2096)
        super().__init__(self.openai_agent) # 这里需要传进去一个 xyz.utils.llm 里的语言模型，目前只有 openai（为了 之后的自驱动做准备，其实也并不是必须的。可以什么也不传。）
        
        self.set_name("mathSolver")
        self.set_description("This is a teacher who can solve math questions.")
        self.set_parameters({"question": {"type": "str", "description": "The question here which need help."}})

        self.llm_cot_agent = LLMAgent(COTMATH, self.openai_agent, inner_multi=False, stream=True)
    
    def flowing(self, question: str) -> str:

        response = self.llm_cot_agent(question=question)

        return response

COTMATH = {
    "system": """Now, you are a Mathematics assistant who can help user to solve the questions.
    """,
    "user": """
Hi! Please solve this question:

{question}  
"""}