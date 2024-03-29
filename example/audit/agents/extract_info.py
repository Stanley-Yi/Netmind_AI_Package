"""
=======
pdf extractor
=======
@date: 2024-3-28
"""

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
print(sys.path)

from dotenv import load_dotenv
from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.utils.llm.openai_client import OpenAIClient
import os
import re
from agents.mathpix import MathpixProcessor
# Load the environment variables from the .env file
load_dotenv()
app_key = os.getenv('mathpix_app_key')
app_id = os.getenv('mathpix_app_id')
mathpix_processor = MathpixProcessor(app_id=app_id, app_key=app_key)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class Extract_info(Agent):
    def __init__(self):
        self.openai_agent = OpenAIClient(api_key=OPENAI_API_KEY, model='gpt-4-0125-preview', temperature=0., top_p=1.0,
                                        max_tokens=2096)
        super().__init__(
            self.openai_agent)  # 这里需要传进去一个 xyz.utils.llm 里的语言模型，目前只有 openai（为了 之后的自驱动做准备，其实也并不是必须的。可以什么也不传。）

        self.set_name("auditSolver")
        self.set_description("This is a audit assistant that extracting information from bank statement.")
        self.set_parameters({"file": {"type": "str", "description": "The latex version of the pdf file"}})

        self.llm_cot_agent = LLMAgent(AUDIT, self.openai_agent, inner_multi=False, stream=False)

    def img2latex(self,image_path):
        """Input: img Filepath, Output: latex string."""
        text, _ = mathpix_processor(image_path=image_path)
        return text 
    
    def extract_dict_from_json(self,text: str):
        """
        Extract the dictionary between "```json" and "```". 
        """
        pattern = r'```json(.*?)```'
        extracted_text = re.findall(pattern, text, re.DOTALL)

        return extracted_text[0].strip()
    
    def flowing(self, image_path: str) -> str:
        text = self.img2latex(image_path)
        response = self.llm_cot_agent(file=text)
        response = self.extract_dict_from_json(response)

        return response


AUDIT = {
    "system": """Now, you are a Audit assistant who can help user to extract information from bank statement.
    ## You must follow all the requirements to modify the draft:
        1. You must extract the name of the bank from this bank statement.
        2. You must extract the name of person from this bank statement .
        3. You must extract the statemtent date from this bank statement.
        4. You must extract the Period Coverd from this bank statement.
        5. You must extract the Opening Balance from this bank statement.
        6. You must extract the Closing Balance from this bank statement.
        7. You must extract all the transactions history from this bank statement.
    
    ## About the output:
        Your output must be a json file containing a python dictionary to store the extracted information in the format looks like this: 
        
        {{
            "bank_name": "xxx",
            "person_name": "xxx",
            "statement_date": "xxx",
            "period_covered": "xxx",
            "opening_balance": "xxx",
            "closing_balance": "xxx",
            "transactions": [
                {{"date": "xxx", "description": "xxx", "credit": "xxx", "debit": "xxx", "balance": "xxx"}},
                # Add more transactions
            ]
        }}
        You must follow all requirements listed above. 
        Your output must contain the json file quoted by "```json" and "```"

    """,
    "user": """
The bank statement is:

{file}
"""}