"""
=======
XYZNode
=======
@file_name: XYZNode.py
@author: Bin Liang
@date: 2023-2-29

"""

# python standard packages
import json
from typing import Any, Dict

# python third-party packages


# import from our operation
from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.node.basic.functional_agent import FunctionalAgent
from xyz.node.operation.Manager import Manager
from xyz.node.operation.InputFormatAgent import InputFormatAgent
from xyz.parameters import core_agent as default_agent
from xyz.utils.llm.core_agent import CoreAgent


class XYZNode(Agent):
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

    def __init__(self,
                 node_config: dict,
                 core_agent: CoreAgent = default_agent) -> None:
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

        # save the common information of the node
        super().__init__(core_agent)

        self.node_config = node_config
        self.name = node_config["name"]
        self.description = node_config["description"]
        self.parameters = node_config["parameters"]
        self.company_role = ""

        # TODO: 留出接口，我们目前要求 parameters 中所有的参数都是必须的
        self.required = list(node_config["parameters"].keys())

        # initialize the agent with different type
        if node_config['node_type'] == "llm":
            self.node = LLMAgent(self.node_config['llm_config']['template'],
                                 self.node_config['llm_config']['generate_parameters'],
                                 core_agent)
        elif node_config['node_type'] == "functional":
            self.node = FunctionalAgent(self.node_config, core_agent)
        elif node_config['node_type'] == "manager":
            self.node = Manager(self.node_config)
        else:
            raise ValueError("node_type is not supported")

        self.input_format_agent = InputFormatAgent(core_agent=core_agent)

    def consciousness(self) -> dict:
        """
        Get the node's consciousness.

        Returns
        -------
        dict
            A dictionary containing the node's consciousness.
        """

        # TODO: 返回一定的信息，对分配任务有帮助的内容
        return {"template": "",
                "job_description": "",
                "momentum": "",
                }

    def set_role(self, role: str) -> None:
        self.company_role = role

    def flowing(self, task: str, **kwargs) -> None:
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

        # TODO: 在自身的数据存储中，会对任务 momentum 进行更新
        response = self.node(**kwargs)

        return response

    def load_memory(self, client, memory_config: dict) -> Any:
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
            # TODO 加载我们需要的 memory， 什么时候加载？怎么使用？
            # self.memory = self.load_memory(self.node_config['memory_config'])
            pass

    def save(self, type="dict", path="") -> Dict[str, str]:
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
            with open(path, "w") as f:
                json.dump(self.node_config, f)
        else:
            raise TypeError("The type is not supported")
