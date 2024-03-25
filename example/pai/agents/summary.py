"""
=======
Summary
=======
@file_name: summary.py
@author: Bin Liang, Tianlei Shi
@date: 2024-3-22
"""


from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent

from example_pai.global_parameters import openai_agent


class Summary(Agent):

    def __init__(self):
        super().__init__(openai_agent)

        self.set_name("Summary")
        self.set_description("This is a teacher which can guide the user to solve the problem step by step.")
        self.set_parameters({"messages": {"type": "list", "description": "The OpenAI messages list which store the "
                                                                         "chat history between the user and assistant."}
                             })

        self.llm_summary_agent = LLMAgent(SUMMARIZE, openai_agent, inner_multi=False, stream=True)

    def flowing(self,  messages: list) -> str:

        if messages is not None:
            return self.llm_summary_agent(messages=messages)


SUMMARIZE = {
    "system": """From now on, you're an experienced teacher.

A student will provide you with a history of dialogue, this dialogue is about help the student to solve a problem. 

Please read the history carefully and generate a summary based on the chat with student.

The content of the summary should include: 
    1. The problem, 
    2. Answer and interface, 
    3. Difficulties based on student's questions and mistake, 
    4. Knowledge points need to be strengthened based on student's questions and mistakes.

You need follow these rules:
1. The summary should be organized as markdown.
2. The summary should be clear and concise.
3. In each part, you need use '## ' to clarify the content.
4. The summary should be based on the student's questions and mistakes, and the knowledge points need to be strengthened.
5. You need be patient and careful to help students analyze the problems, you are not allowed to make any mistakes.

    """,
    "user": """
Hi, teacher. Please help me to summarize the history of dialogue. 
"""}
