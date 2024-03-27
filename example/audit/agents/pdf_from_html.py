"""
=======
pdf generator
=======
@date: 2024-3-22
"""
import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
print(sys.path)

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import pdf2image
import numpy as np
import cv2
from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.utils.llm.openai_client import OpenAIClient
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class Gen_pdf(Agent):
    def __init__(self):
        self.openai_agent = OpenAIClient(api_key=OPENAI_API_KEY, model='gpt-4-0125-preview', temperature=0., top_p=1.0,
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
    
# Example data, including transactions and other dynamic content
data = {
    "Account_Number": "123-456-789",
    "Statement_Date": "2024-03-01",
    "Period_Covered": "2024-02-01 to 2024-02-29",
    "name": "John Doe",
    "address_line1": "2450 Courage St, STE 108",
    "address_line2": "Brownsville, TX 78521",
    "Opening_Balance": "175,800.00",
    "Total_Credit_Amount": "510,000.00",
    "Total_Debit_Amount": "94,000.00",
    "Closing_Balance": "591,800.00",
    "Account_Type": "Savings",
    "Number_Transactions": "10",
    "transactions": [
        {"Date": "2024-03-01", "Description": "Coffee Shop", "Credit": "$50.00", "Debit": "-$5.00", "Balance": "$995.00"},
        # More transactions
    ]
}