""" 
========
ABSAgent
========
@file_name: ABSAgent.py
@author: Bin Liang
@date: 2024-3-1

"""


from abc import ABC, abstractmethod


class ABSAgent(ABC):

    @abstractmethod
    def run(self, content:str) -> str:
        pass
    
    
    
    