""" 
=======
Company
=======
@file: Company.py
@author: Bin Liang
@date: 2023-2-29

"""


# python standard packages


# python third-party packages


# import from our modules
from xyz.parameters import logger


class Company:
    
    def __init__(self, nodes_list, auto=False ):
        """
        TODO: 考虑一下同步 异步的事情
        自动/手动
        feedback 自我改进
        """
        
        self.auto = auto
        if not auto:
            self.start = nodes_list[0]
            for i in range(len(nodes_list) - 1):
                self._add_connection(nodes_list[i], nodes_list[i+1])

    def __str__(self, *args, **kwds):
        raise NotImplementedError
    
    def working(self, task:str) -> None:
        
        if not self.auto:
            result = self._artificial_working(task)
        else:
            raise TypeError("We do not complete the task automatically. Please set auto=False.")
        return result
    
    def _add_connection(self, node_1, node_2) -> None:
        node_1.point_to(node_2)
        
    def _artificial_working(self, task:str) -> None:
        
        node = self.start
        while node.point:
            process = node.working(task)
            node = node.point[0]
            task += process
            
        result = node.working(task)
        return result
            
    def save(self) -> None:
        raise NotImplementedError
    
    
    