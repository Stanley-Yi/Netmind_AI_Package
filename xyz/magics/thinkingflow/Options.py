""" 
=======
Options
=======
@file_name: Options.py
@author: Bin Liang
@date: 2024-2-23

"""


from xyz.magics.thinkingflow.ThinkingFlow import ThinkingFlow
from xyz.magics.agent.CoreAgent import CoreAgent

class Options(ThinkingFlow):
    
    def __init__(self):
        
        ThinkingFlow.__isabstractmethod__ = True

    def process(self):
        pass
    
    def _get_options(self):
        pass
    
    def _summary(self):
        pass
    
    