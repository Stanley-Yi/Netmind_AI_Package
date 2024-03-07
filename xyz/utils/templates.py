""" 
=========
templates
=========
@file_name: templates.py
@author: Bin Liang
@date: 2024-3-7

"""


class Templates:
    
    def __init__(self, logger):
        raise NotImplementedError
        
    def __call__(self, type):
        raise NotImplementedError
    
    def get_functional_config(self):
        raise NotImplementedError
    
    def get_llm_config(self):
        raise NotImplementedError

