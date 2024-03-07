""" 
========
Planning
========
@file_name: Planning.py
@author: Bin Liang
@date: 2024-2-23

"""


from xyz.magics.thinkingflow.ThinkingFlow import ThinkingFlow
from xyz.node.CoreAgent import CoreAgent

class Planning(ThinkingFlow):
    
    def __init__(self):
        ThinkingFlow.__isabstractmethod__ = True

    def process(self):
        pass
    
    def _planning(self):
        pass
    
    def _summary(self):
        pass
    
