""" 
============
ThinkingFlow
============
@file_name: ThinkingFlow.py
@author: Bin Liang
@date: 2024-2-23

"""


from abc import ABC, abstractmethod


class ThinkingFlow(ABC):
    
    @abstractmethod
    def process(self):
