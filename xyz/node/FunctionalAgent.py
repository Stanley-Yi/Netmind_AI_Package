""" 
===============
FunctionalAgent
===============
@file_name: FunctionalAgent.py
@author: Bin Liang
@date: 2023-2-29

"""



class FunctionalAgent:
    
    
    def __init__(self, config):
        raise NotImplementedError

    def __call__(self, *args, **kwds):
        raise NotImplementedError
    
    def run(self, content:str) -> str:
        raise NotImplementedError
    
    def get_api_format(self, function_name:str) -> str:
        raise NotImplementedError


