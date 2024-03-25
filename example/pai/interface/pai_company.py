"""
==========
PaiCompany
==========
@file_name: pai_company.py
@date: 2024-3-20
@author: Bin Liang, Tianlei
"""


from xyz.node.agent import Agent

from pai.agents.search_answer import SearchAnswer
from pai.agents.course_classify import CourseClassify
from pai.agents.generate_process import GenerateProcess
from pai.agents.guidance_chat import GuidanceChat
from pai.agents.summary import Summary
from pai.interface.pai_company_utils import stream_print


class PaiCompany(Agent):

    def __init__(self):
        super().__init__()

        self.set_name("PaiCompany")
        self.set_description("This is a teacher which can guide the user to solve the problem step by step.")
        self.set_parameters({"question": {"type": "str", "description": "The question here which need help."},
                             "images": {"type": "str", "description": "The image of this question."}})

        self.search_answer = SearchAnswer()
        self.course_classify = CourseClassify()
        self.generate_process = GenerateProcess()
        self.guidance_chat = GuidanceChat()
        self.summary = Summary()

    def flowing(self, question: str, images=None):
    
        course = self.course_classify(question=question)
        question_info = self.search_answer(question=question, images=images, course=course)

        answer = question_info["answer"]
        question = question_info["question"]

        if question_info["process"] == "":
            process = self.generate_process(question=question, answer=answer)
            question_info["process"] = process

        messages = []
        in_progress = True
        
        while in_progress:

            user_input = ""
            response = self.guidance_chat(question=question,
                                          answer=question_info["answer"],
                                          content=user_input, 
                                          process=question_info["process"],
                                          messages=messages)
            assistant_content, finish_signal = stream_print(response, "##||&&")
            
            if finish_signal:
                response = self.summary(messages=messages)
                assistant_content, in_progress = stream_print(response)
                messages.append({"role": "assistant", "content": assistant_content})
                break
            else:
                messages.append({"role": "assistant", "content": assistant_content})

            user_input = input("\nUser: ")
            messages.append({"role": "user", "content": user_input})
            if "end" in user_input:
                break

        return messages
