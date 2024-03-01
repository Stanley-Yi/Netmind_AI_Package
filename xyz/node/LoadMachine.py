""" 
===========
LoadMachine
===========
@file_name: LoadMachine.py
@author: Bin Liang
@date: 2024-3-1

"""


class LoadMachine:
    
    
    def __init__(self, config_path):
        raise NotImplementedError


    def __call__(self, *args, **kwds):
        raise NotImplementedError
    
    def get_config(self, config_path:str) -> str:
        raise NotImplementedError

