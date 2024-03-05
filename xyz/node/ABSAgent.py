""" 
========
ABSAgent
========
@file_name: ABSAgent.py
@author: Bin Liang
@date: 2024-3-1

"""


from abc import ABC, abstractmethod


class Supervisor(ABC):
    
    def __init__(self, config):
        raise NotImplementedError

    def __call__(self, *args, **kwds):
        raise NotImplementedError

    @abstractmethod
    def run(self, content:str) -> str:
        pass
    
    @abstractmethod
    def save(self) -> None:
        pass
    
    
    