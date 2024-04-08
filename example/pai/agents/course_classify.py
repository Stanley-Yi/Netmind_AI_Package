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

from global_parameters import openai_agent


class CourseClassify(Agent):

    def __init__(self):
        super().__init__()

        # self.set_name("GuidanceTeacher")
        # self.set_description("This is a teacher which can guide the user to solve the problem step by step.")   # TODO: description
        # self.set_parameters({"question": {"type": "str", "description": "The question here which need help."}}) # TODO: Input
        # self.set_output({"category": {"type": "str", "description": "The category of the question."}})  # TODO: Output

        self.llm_course_classify = LLMAgent(COURSE_CLASSIFY, openai_agent, stream=False)

    def flowing(self, question: str) -> str:

        response = self.llm_course_classify(question=question)

        return response


COURSE_CLASSIFY = [
    
    {"role" : "system", "content" : """I will provide you with a question, please help me to classify the question.
There are valid categories:
Mathematics, Physics, Chemistry, Biology, Economics, Technology

Please only return the category to which the question belongs, without extra letters, symbols, or spaces. 
The returned category must be one of the valid categories.
"""
    },
    
    {"role": "user", "content" : """
Hi! Please classify this question:

{question}  ss
"""
    }
]
