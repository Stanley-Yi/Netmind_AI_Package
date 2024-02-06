""" 
============
ThinkingFlow
============
Using multi-agents to build a thinking-flow to process the complex tasks.
"""


from xyz.magics.agent.CoreAgent import CoreAgent


# 这个class 目前是专门服务于 consciousness & momentum 的
class ThinkingFlow():
    
    def __init__(self, agents_dict):
        self.agents_dict = agents_dict 
        
    # To Hongyi： 先按咱的老方法去做 Thinking-Flow。用固定的对象方法来表达。
    def run(self, **kwargs):
        """
        Run the thinking-flow to process the complex tasks.
        """

        raise NotImplementedError

