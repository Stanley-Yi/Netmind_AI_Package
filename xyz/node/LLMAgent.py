""" 
========
LLMAgent
========
@file_name: LLMAgent.py
@author: Bin Liang
@date: 2023-2-29

"""


from xyz.magics.agent.CoreAgent import CoreAgent
from xyz.magics.thinkingflow.ThinkingFlow import ThinkingFlow


class LLMAgent(CoreAgent):
    
    
    def __init__(self, config):
        raise NotImplementedError


    def __call__(self, *args, **kwds):
        raise NotImplementedError
    
    def using_thinking_flow(self, thinking_flow:ThinkingFlow):
        raise NotImplementedError
    
    def run(self, content:str) -> str:
        raise NotImplementedError
    
    
