""" 
====
Node
====
@file_name: XYZNode.py
@author: Bin Liang 
@date: 2024-2-23

"""


class Node:
    
    def __init__(
            self,
            task_name: str,
            task_desc: str,
            task_type: int,
            memory: object, 
            momentum: object,
            consicious: object,
            ):
        """ The basic node object, which consists of memory, momentum and consiciousness.
           
            Parameters
            ----------
            task_type : int
                if task_type = 0, then the solving path is pre-defined.
                If task_type = 1, then the solving path is not pre-defined, and the solving path is determined by the consiciousness.
        """

        self.task = task_name
        self.task_desc = task_desc
        self.task_type = task_type
        self.memory = memory
        self.momentum = momentum
    
        self.consicious = consicious

        # Step 1: chekc the task type
        if task_type == 1:
            self.solving_path = self.consicious.set_task(self.task_name, self.task_desc)
        
    def run(
            self, 
            ):
        """run the task, and return the result
           self.solving_Path is the solving path, which is a list of node that the task will go through.
           consicious would remember the path
        """ 
        result = self.solving_path.run(self.task_name, self.task_desc)
        self.consicious.add_task(self.task_name, self.task_desc,self.solving_path)

        return result

