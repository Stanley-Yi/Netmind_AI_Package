""" 
=======
Options
=======
@file_name: Options.py
@author: Bin Liang
@date: 2024-2-23

"""


from xyz.elements.thinkingflow.ThinkingStructure import ThinkingStructure


class Options(ThinkingStructure):
    
    def __init__(self):
        
        ThinkingStructure.__isabstractmethod__ = True

    def process(self):
        pass
    
    def _get_options(self):
        pass
    
    def _summary(self):
        pass
    
    