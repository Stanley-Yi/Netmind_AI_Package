"""
===============
AutoMathCompany
===============
@file_name: auto_math_company.py
@author: Bin Liang
@date: 2024-04-13

"""


import argparse 

from xyz.graph.auto_company import AutoCompany
from xyz.utils.openai_client import OpenAIClient

from example.auto_math.agents.plan_agent import PlanAgent
from example.auto_math.agents.solving_agent import SolvingAgent
from example.auto_math.agents.summary_agent import SummaryAgent
from example.auto_math.agents.coding_agent import CodingAgent


def set_args():
    
    parser = argparse.ArgumentParser(description="Auto Math Company")
    parser.add_argument("--api_key", type=str, default="", help="OpenAI API Key")
    parser.add_argument("--question", type=str, default="", help="The question which need help.")
    
    return parser.parse_args()


if __name__ == "__main__":
    
    args= set_args()
    
    llm_client = OpenAIClient(api_key=args.api_key)
    
    plan_agent = PlanAgent(llm_client)
    solving_agent = SolvingAgent(llm_client)
    summary_agent = SummaryAgent(llm_client)
    coding_agent = CodingAgent(llm_client)
    
    staffs = [plan_agent, solving_agent, summary_agent, coding_agent]
    
    company = AutoCompany(llm_client=llm_client)
    
    company.add_agents(staffs)
    
    company(question=args.question)
