"""
====
Node
====
@file_name: Node.py 
@author: Bin Liang
@date: 2023-2-29

"""


# python standard packages
import json
from typing import Any

# python third-party packages


# import from our modules
from xyz.node.LLMAgent import LLMAgent
from xyz.node.FunctionalAgent import FunctionalAgent
from xyz.node.Manager import Manager


class Node:
    """ 
    A node that can be of different types (LLM, functional, manager) based on the configuration.
    This code implements a Dependency Injection (DI) pattern that allows for combining different agents and utilizing their methods.

    Parameters
    ----------
    node_config : dict
        The configuration for the node. It should contain the key 'node_type' which can be "llm", "functional", or "manager".
    core_agent : CoreAgent
        The core agent to use for requesting response from OpenAI.
    """
    
    def __init__(self, node_config:dict, core_agent) -> None:
        """ 
        Initialize the Node.

        Parameters
        ----------
        node_config : dict
            The configuration for the node. It should contain the key 'node_type' which can be "llm", "functional", or "manager".
        core_agent : CoreAgent
            The core agent to use for requesting response from OpenAI.

        Raises
        ------
        ValueError
            If the node type is not supported.
        """
        
        # save the information of the node
        self.node_config = node_config
        
        # initialize the agent with different type
        if node_config['node_type'] == "llm": 
            self.node = LLMAgent(self.node_config, core_agent)   
        elif node_config['node_type'] == "functional":    
            self.node = FunctionalAgent(self.node_config, core_agent)  
        elif node_config['node_type'] == "manager":
            self.node = Manager(self.node_config)
        else:
            raise ValueError("node_type is not supported")
            
    def __str__(self) -> Any:
        """
        Get a string representation of the node.

        Returns
        -------
        str
            A string representation of the node.
        """
        
        # TODO: 需要精细化完善，考虑到 自驱动时需要 由 llm 进行粘合
        if self.node_config['node_type'] == "llm":
            return self.node_config['description'] + self.node_config['template'] 
        elif self.node_config['node_type'] == "functional":
            
            return self.node_config['description'] + self.node.get_function_call_info()
        
    def get_info():
        # TODO: 为了能让 manager 能够获取到更多的信息，我们需要在这里返回node的具体信息。
        # 这个功能服务于自驱动
        raise NotImplementedError
    
    def load_memory(self, client, memory_config:dict) -> Any:
        """
        Load the node's memory.

        Parameters
        ----------
        client : object
            The client to use for loading the memory.
        memory_config : dict
            The configuration for the memory.
        """
        
        # 这一步 应该在 初始化 company 的时候进行，每一个 company 共用一个 client
        if self.node_config['memory_config']:
            # TODO 加载我们需要的 memory
            # self.memory = self.load_memory(self.node_config['memory_config'])
            pass
    
    def consciousness(self) -> str:
        """
        Get the node's consciousness.

        Returns
        -------
        dict
            A dictionary containing the node's consciousness.
        """
        
        # TODO: 返回一定的信息，对分配任务有帮助的内容
        return {"template": "",
                "job_description" : "",
                "momentum" : "",
                }
    
    def working(self, task:str, **kwargs ) -> None:
        """ 
        Assign a task to the node.

        Parameters
        ----------
        task : str
            The task to assign to the node.
        **kwargs
            The keyword arguments to use for running the task.

        Returns
        -------
        str
            The response from the node.
        """
        
        # TODO: 在自身的数据存储中，会对任务进行更新
        response = self.node(**kwargs)
        
        return response
    
    def save(self, type="dict", path="") -> None:
        """
        Save the node's data.

        Raises
        ------
        NotImplementedError
            If the method is not implemented.
        """
        
        if type == "dict":
            return self.node_config
        elif type == "json":
            with open (path, "w") as f:
                json.dump(self.node_config, f)
        else:
            raise TypeError("The type is not supported")
        
    