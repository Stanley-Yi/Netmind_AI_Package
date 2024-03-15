""" 
============
ThinkingFlow
============
Using multi-agents to build a thinking-flow to process the complex tasks.
"""


# 这个class 目前是专门服务于 consciousness & momentum 的
class ThinkingFlow():
    
    def __init__(self, agents_dict):
        self.agents_dict = agents_dict 
    
    def _set_template(self):

        system = self.template["System"]
        user = self.template["Human"]
        
        self.prompts = system + "||--||" + user

    # To Hongyi： 先按咱的老方法去做 Thinking-Flow。用固定的对象方法来表达。
    def run(self, **kwargs):
        """
        Run the thinking-flow to process the complex tasks.
        """
        prefix = self.prompts.format(**kwargs)
        raise NotImplementedError

