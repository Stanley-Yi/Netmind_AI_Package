""" 
==========
Supervisor
==========
@file_name: Supervisor.py
@author: Bin Liang
@date: 2024-3-1

"""


class Supervisor:
    
    
    def __init__(self, config):
        raise NotImplementedError

    def __call__(self, *args, **kwds):
        raise NotImplementedError

    def run(self, content:str) -> str:
        raise NotImplementedError

    def save(self) -> None:
        raise NotImplementedError