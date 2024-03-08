""" 
========
Planning
========
@file_name: Planning.py
@author: Bin Liang
@date: 2024-2-23

"""


from xyz.node.CoreAgent import CoreAgent
from xyz.magics.thinkingflow.ThinkingStructure import ThinkingStructure


class Planning(ThinkingStructure):
    
    def __init__(self):
        ThinkingStructure.__isabstractmethod__ = True

    def process(self):
        pass
    
    def _planning(self):
        pass
    
    def _summary(self):
        pass
    
