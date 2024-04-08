"""
=====
Agent
=====
@file_name: agent.py
@author: Bin Liang
@date: 2024-3-15
"""


from typing import Dict, Callable
from xyz.node.agent import Agent

__all__ = ["Staff"]


class Staff(Agent):
    name: str
    description: str
    parameters: Dict[str, str]
    output: Dict[str, str]
    required: list
    input_format_agent: None
    template: str

    def __init__(self, core_agent) -> None:
        super().__init__()

        self.input_format_agent = None
        self.core_agent = core_agent

        super().__setattr__("name", "")
        super().__setattr__("description", str)
        super().__setattr__("parameters", {})
        super().__setattr__("output", {})
        super().__setattr__("required", [])
        super().__setattr__("type", "agent")
        super().__setattr__("input_format_agent", None)

    def _wrap_call(self, **kwargs) -> Callable:
        # TODO: Preparing for hooks part. For example, we can add a hook to see the interface.

        if "auto" in kwargs:
            auto = kwargs.pop("auto")
        else:
            auto = False

        if "node_input" in kwargs:
            node_input = kwargs.pop("node_input")
        else:
            node_input = ""

        if auto:
            print(f"Agent {self.name} auto get the parameters")
            if node_input == "":
                raise ValueError("The input is empty. You must give me the whole input from the last node.")
            try:
                parameters = self.format_input(node_input)
            except:
                raise ValueError("You need identify a InputFormatAgent as a attribute of the node.")
            return self.flowing(**parameters)
        else:
            return self.flowing(**kwargs)

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
    def as_tool(self) -> Dict:
        return self.tools_format()

    def format_input(self, input: str) -> Dict[str, str]:
        """
        Format the input for the node.

        Parameters
        ----------
        input : str
            The input to format.

        Returns
        -------
        dict
            The formatted input.
        """

        tools = [self.as_tool]
        _, parameters = self.input_format_agent(tools=tools, input=input)
        return parameters

    def add_input_format_agent(self, input_format_agent) -> None:
        self.input_format_agent = input_format_agent

