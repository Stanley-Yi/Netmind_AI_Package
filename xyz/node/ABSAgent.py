""" 
========
ABSAgent
========
@file_name: ABSAgent.py
@author: Bin Liang
@date: 2024-3-1

"""


# python standard packages


# python third-party packages
from abc import ABC, abstractmethod

# python first-party packages


class ABSAgent(ABC):

    @abstractmethod
    def run(self, content:str) -> str:
        pass
    
    