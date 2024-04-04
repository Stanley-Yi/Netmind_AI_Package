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
import json
import re
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class Gen_pdf(Agent):
    def __init__(self):
        
        super().__init__()  

        self.set_name("bank_statementGenerator")
        self.set_description("This is a pdf generator to generate pdf given html template.")
        self.set_parameters({"pdf_path": {"type": "str", "description": "The path to store pdf."},
                             "img_path": {"type": "str", "description": "The path to store img."},
                             "html_path": {"type": "str", "description": "The path to load trml template."}})

        self.openai_agent = OpenAIClient(api_key=OPENAI_API_KEY, model='gpt-4-0125-preview', temperature=0.7, top_p=0.8,
                                         max_tokens=2096)
        self.llm_bank_agent = LLMAgent(BANK_INFO, self.openai_agent, inner_multi=False, stream=False)

    def pdftopages(self,pdf_path):
        """Input: PDF Filepath, Output: List of Page objects."""
        pil_pages = pdf2image.convert_from_path(pdf_path)
        #save_pil_images(pil_pages, os.path.join(local_store_folder, self.name + "pages"))
        page_imgs = [cv2.cvtColor(np.asarray(p), cv2.COLOR_RGB2BGR) for p in pil_pages]
        return page_imgs
    
    def extract_dict_from_json(self,text: str):
        """
        Extract the dictionary between "```json" and "```". 
        """
        pattern = r'```json(.*?)```'
        extracted_text = re.findall(pattern, text, re.DOTALL)

        return extracted_text[0].strip()

    def flowing(self, history: str, pdf_path: str, img_path: str,html_path: str) -> str:
        
        data = self.llm_bank_agent(messages=[], history=history)
        
        data_clean = self.extract_dict_from_json(data)
        data_clean = json.loads(data_clean)
        env = Environment(loader=FileSystemLoader(''))
        template = env.get_template(html_path)
        html_content = template.render(**data_clean)
        # Generate PDF
        HTML(string=html_content).write_pdf(pdf_path)
        # convert pdf to images
        imgs = self.pdftopages(pdf_path)
        cv2.imwrite(img_path, imgs[0])

        return data_clean
    
    def template(self, data: str, pdf_path: str, img_path: str,html_path: str) -> None:
 
        env = Environment(loader=FileSystemLoader(''))
        template = env.get_template(html_path)
        html_content = template.render(**data)
        # Generate PDF
        HTML(string=html_content).write_pdf(pdf_path)
        # convert pdf to images
        imgs = self.pdftopages(pdf_path)
        cv2.imwrite(img_path, imgs[0])


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
        {"Date": "2024-03-01", "Description": "Online Purchase", "Credit": "$121.51", "Debit": "-", "Balance": "$1,116.51"}, 
        {"Date": "2024-03-02", "Description": "Coffee Shop", "Credit": "$143.06", "Debit": "-", "Balance": "$1,259.57"}, 
        {"Date": "2024-03-03", "Description": "Utility Bill", "Credit": "-", "Debit": "-$60.72", "Balance": "$1,198.85"}, 
    ]
}

BANK_INFO = [
    {"role" : "system",
     "content": """Now, you are a Banking assistant who can help user to generate logical user information for bank statement.
Here is a sample of information that you need to follow:
{{
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
        {{"Date": "2024-03-01", "Description": "Coffee Shop", "Credit": "$50.00", "Debit": "-$5.00", "Balance": "$995.00"}},
        {{"Date": "2024-03-01", "Description": "Online Purchase", "Credit": "$121.51", "Debit": "-", "Balance": "$1,116.51"}}, 
        {{"Date": "2024-03-02", "Description": "Coffee Shop", "Credit": "$143.06", "Debit": "-", "Balance": "$1,259.57"}}, 
        {{"Date": "2024-03-03", "Description": "Utility Bill", "Credit": "-", "Debit": "-$60.72", "Balance": "$1,198.85"}}, 
    ]
}}
## You must follow all the requirements to modify the draft:
    1. You must generate information given in the sample, including "Account_Number", "Statement_Date", etc.  
    2. You must generate several "transactions", the number could vary.
    3. You must generate logical values, the "Statement_Date", "Period_Covered" and "Date" in "transactions" must be resaonable.
    4. You must generate unique user information, not seen in the history. 

## About the output:
    Your output must be a json file containing a python dictionary to store the extracted information in the format looks like the sample above. 
    You must follow all requirements listed above. 
    Your output must contain the json file quoted by "```json" and "```"

    """},
    {"role": "user",
    "content": """
        Here is the history: {history}. 
"""}]
