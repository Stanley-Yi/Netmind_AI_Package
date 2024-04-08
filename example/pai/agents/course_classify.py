"""
==============
CourseClassify
==============
@file_name: course_classify.py
@author: Bin Liang, Tianlei Shi
@date: 2024-3-22
"""


__all__ = ["CourseClassify"]

from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent


class CourseClassify(Agent):
    information: dict
    llm_course_classify: LLMAgent

    def __init__(self, openai_agent):
        super().__init__()

        self.set_information({
            "type": "function",
            "function": {
                "name": "GuidanceTeacher",
                "description": "This is a teacher which can guide the user to solve the problem step by step.",
                "parameters": {"question": {"type": "str", "description": "The question here which need help."}},
                "required": ["question"],
            },
        })

        self.llm_course_classify = LLMAgent(COURSE_CLASSIFY, openai_agent, stream=False)

    def flowing(self, question: str) -> str:
        """
        Call the function to classify the question in the course: Mathematics, Physics, Chemistry,
        Biology, Economics, Technology

        Parameters
        ----------
        question: str
            The question which need to be classified.

        Returns
        -------
        str
            The category of the question of which in the courses.
        """

        response = self.llm_course_classify(question=question)

        return response


COURSE_CLASSIFY = [

    {"role": "system", "content": """I will provide you with a question, please help me to classify the question.
There are valid categories:
Mathematics, Physics, Chemistry, Biology, Economics, Technology

Please only return the category to which the question belongs, without extra letters, symbols, or spaces. 
The returned category must be one of the valid categories.
"""
     },

    {"role": "user", "content": """
Hi! Please classify this question:

{question}  ss
"""
     }
]
