"""
====
Node
====
@file_name: Node.py 
@author: Bin Liang
@date: 2023-2-29

"""


from typing import Any
from xyz.node.LLMAgent import LLMAgent
from xyz.node.FunctionalAgent import FunctionalAgent


class Node:
    
    def __init__(self, node_config:dict) -> None:
        """ 
        DI
        """
        
        # 
        self.node_config = node_config
        
        # 
        if node_config['node_type'] == "llm": 
            self.node = LLMAgent(self.node_config)   
        elif node_config['node_type'] == "functional":    
            self.node = FunctionalAgent(self.node_config)  
        else:
            raise ValueError("node_type is not supported")
            
    def __type__(self) -> Any:
        return self.node_config['node_type'] + "_node"
    
    def load_memory(self, client, memory_config:dict) -> Any:
        # 这一步 应该在 初始化 company 的时候进行，每一个 company 共用一个 client
        if self.node_config['memory_config']:
            self.memory = self.load_memory(self.node_config['memory_config'])
    
    def cosciousness(self) -> str:
        
        # TODO: 返回一定的信息，对分配任务有帮助的内容
        
        
        return {"template": "",
                "job_description" : "",
                "momentum" : "",
                }
    
    def working(self, content:str) -> None:
        """ 
        任务分配
        """
        
        response = self.node.run(content)
        
        return response
    
    def save(self) -> None:
        raise NotImplementedError
        
    