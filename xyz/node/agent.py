"""
====
Node
====
@file_name: agent.py
@author: Bin Liang
@date: 2024-3-15

"""

from typing import Dict, Callable, Any
from abc import abstractmethod

# from xyz.node.operation.InputFormatAgent import InputFormatAgent
from xyz.utils.llm.dummy_llm import dummy_agent as default_agent

__all__ = ["Agent"]


class Agent:
    name: str
    description: str
    parameters: Dict[str, str]
    required: list
    # input_format_agent: InputFormatAgent
    template: str

    def __init__(self, core_agent=default_agent) -> None:
        # TODO: Careful with this. You'd better use super().__init__(core_agent)
        # self.input_format_agent = InputFormatAgent(core_agent)
        self.core_agent = core_agent

        super().__setattr__("name", "")
        super().__setattr__("description", "")
        super().__setattr__("parameters", {})
        super().__setattr__("required", [])
        super().__setattr__("type", "agent")

    def _wrap_call(self, auto=False, node_input="", **kwargs) -> Callable:
        # TODO: Preparing for hooks part. For example, we can add a hook to see the interface.

        if auto:
            print(f"Agent {self.name} auto get the parameters")
            if node_input == "":
                raise ValueError("The input is empty. You must give me the whole input from the last node.")
            parameters = self.format_input(node_input)
            return self.flowing(**parameters)
        else:
            return self.flowing(**kwargs)

    __call__: Callable[..., Any] = _wrap_call
    
    @abstractmethod
    def flowing(self, *args, **kwargs) -> Any:
        """
        We can use the overload for multimodal
        """
        ...

    def __str__(self) -> str:

        info = f"Agent(name={self.name}, description={self.description}, parameters={self.parameters})"

        for key, value in vars(self).items():
            try:
                if "type" in vars(value) and value.type == "agent":
                    info += f"\n\n\t[SubAgent: {key}: {value._structure(2)}]"
            except:
                pass

        return info
    
    def _structure(self, order):

        pre_blank = "\t"*order
        info = f"{pre_blank}Agent(name={self.name}, description={self.description}, parameters={self.parameters})"

        for key, value in vars(self).items():
            try:
                if "type" in vars(value) and value.type == "agent":
                    info += f"\n{pre_blank}[SubAgent: {key}: {value._structure(order+1)}]"
            except:
                pass

        return info

    def set_name(self, name: str) -> None:
        self.name = name

    def set_description(self, description: str) -> None:
        self.description = description

    def set_parameters(self, parameters: Dict[str, Dict]) -> None:
        self.parameters = parameters
        self.required = [key for key in self.parameters.keys()]


    def tools_format(self) -> Dict[str, str]:

        if self.description == "":
            raise ValueError("The description of the node is empty.")

        if self.parameters == {}:
            raise ValueError("The parameters of the node is empty.")
        else:
            self.required = [key for key in self.parameters.keys()]

        request_info = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "required": self.required,
            },
        }

        return request_info

    @property
    def as_tool(self) -> Dict[str, str]:
        return self.tools_format()
