"""
==============
CourseClassify
==============
@file_name: course_classify.py
@author: Bin Liang, Tianlei Shi
@date: 2024-3-22
"""


from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent

from example.pai.global_parameters import openai_agent


class CourseClassify(Agent):

    def __init__(self):
        super().__init__(openai_agent)

        self.set_name("GuidanceTeacher")
        self.set_description("This is a teacher which can guide the user to solve the problem step by step.")
        self.set_parameters({"question": {"type": "str", "description": "The question here which need help."}})

        self.llm_course_classify = LLMAgent(COURSE_CLASSIFY, openai_agent, inner_multi=False, stream=False)

    def flowing(self, question: str) -> str:

        response = self.llm_course_classify(question=question)

        return response


COURSE_CLASSIFY = {
    "system": """I will provide you with a question, please help me to classify the question.
There are valid categories:
Mathematics, Physics, Chemistry, Biology, Economics, Technology

Please only return the category to which the question belongs, without extra letters, symbols, or spaces. 
The returned category must be one of the valid categories.
    """,
    "user": """
Hi! Please classify this question:

{question}  
"""}
