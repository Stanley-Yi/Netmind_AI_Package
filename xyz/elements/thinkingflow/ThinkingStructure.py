""" 
=================
ThinkingStructure
=================
@file_name: ThinkingStructure.py
@author: Bin Liang
@date: 2024-2-23

"""


from abc import ABC, abstractmethod


class ThinkingStructure(ABC):
    
    @abstractmethod
    def process(self):
        pass
